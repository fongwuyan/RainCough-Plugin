package server

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"

	"accountpool/internal/model"
	"accountpool/internal/pool"
)

type streamUsage struct {
	Prompt     int
	Completion int
	Total      int
	Reason     string
}

type streamEmitter interface {
	Start(w http.ResponseWriter)
	Delta(text string)
	End(u streamUsage)
}

func (s *Server) crossStream(w http.ResponseWriter, r *http.Request, proto string, req canonicalReq,
	tok *model.Token, start time.Time) bool {
	failed := map[string]bool{}
	for attempt := 0; attempt < 3; attempt++ {
		sel, err := s.Pool.Select(req.Model, failed)
		if err != nil {
			return false
		}
		usage, ok := s.streamCanonical(w, r, sel, req, proto)
		s.Pool.Release(sel.Account.ID)
		if !ok {
			failed[sel.Account.ID] = true
			continue
		}
		s.Pool.MarkOK(sel.Account.ID)
		s.recordUsage(tok.ID, sel, req.Model, usage.Prompt, usage.Completion, usage.Total,
			time.Since(start).Milliseconds(), 200, "")
		return true
	}
	return false
}

func (s *Server) streamCanonical(w http.ResponseWriter, r *http.Request, sel *pool.Selection,
	req canonicalReq, proto string) (streamUsage, bool) {
	var url string
	var body []byte
	headers := map[string]string{}
	switch sel.Provider.Type {
	case "anthropic":
		url = anthropicMessagesURL(sel.Provider.BaseURL)
		body = buildAnthropicStreamRequest(req)
		headers["x-api-key"] = sel.Key
		headers["anthropic-version"] = "2023-06-01"
	case "gemini":
		url = geminiURL(sel.Provider.BaseURL, "models/"+req.Model+":streamGenerateContent", sel.Key, true)
		body = buildGeminiRequest(req)
	default:
		url = chatURL(sel.Provider.BaseURL)
		if sel.Provider.Type == "azure" {
			url = strings.TrimRight(sel.Provider.BaseURL, "/") + "/chat/completions?api-version=2024-10-21"
			headers["api-key"] = sel.Key
		} else {
			headers["Authorization"] = "Bearer " + sel.Key
		}
		body = buildOpenAIRequest(req, true)
	}
	upReq, err := http.NewRequestWithContext(r.Context(), http.MethodPost, url, strings.NewReader(string(body)))
	if err != nil {
		s.Pool.Cooldown(sel.Account.ID, 30, err.Error())
		return streamUsage{}, false
	}
	upReq.Header.Set("Content-Type", "application/json")
	upReq.Header.Set("Accept", "text/event-stream, application/json")
	for k, v := range headers {
		upReq.Header.Set(k, v)
	}
	resp, err := s.Client.Do(upReq)
	if err != nil {
		s.Pool.Cooldown(sel.Account.ID, 60, trimErr(err.Error()))
		return streamUsage{}, false
	}
	defer resp.Body.Close()
	if resp.StatusCode >= 400 {
		raw, _ := io.ReadAll(io.LimitReader(resp.Body, 4096))
		s.Pool.Cooldown(sel.Account.ID, nativeCooldown(resp.StatusCode), string(raw))
		return streamUsage{}, false
	}

	em := newEmitter(proto)
	em.Start(w)
	usage := streamUsage{}
	ct := resp.Header.Get("Content-Type")
	if !strings.Contains(ct, "event-stream") {
		// 某些网关对 stream=true 仍返回完整 JSON：解析后一次性下发。
		raw, _ := io.ReadAll(io.LimitReader(resp.Body, 32<<20))
		parsed := parseProviderResponse(sel.Provider.Type, raw)
		if parsed.Text != "" {
			em.Delta(parsed.Text)
		}
		usage = streamUsage{Prompt: parsed.PromptTokens, Completion: parsed.CompletionTokens,
			Total: parsed.TotalTokens, Reason: parsed.FinishReason}
		em.End(usage)
		return usage, true
	}

	err = readSSE(resp.Body, func(data []byte) {
		switch sel.Provider.Type {
		case "anthropic":
			var v struct {
				Type  string `json:"type"`
				Delta struct {
					Type       string `json:"type"`
					Text       string `json:"text"`
					StopReason string `json:"stop_reason"`
				} `json:"delta"`
				Message struct {
					Usage struct {
						InputTokens int `json:"input_tokens"`
					} `json:"usage"`
				} `json:"message"`
				Usage struct {
					InputTokens  int `json:"input_tokens"`
					OutputTokens int `json:"output_tokens"`
				} `json:"usage"`
			}
			if json.Unmarshal(data, &v) != nil {
				return
			}
			switch v.Type {
			case "content_block_delta":
				if v.Delta.Type == "" || v.Delta.Type == "text_delta" {
					em.Delta(v.Delta.Text)
				}
			case "message_start":
				usage.Prompt = v.Message.Usage.InputTokens
			case "message_delta":
				usage.Completion = v.Usage.OutputTokens
				if v.Delta.StopReason != "" {
					usage.Reason = v.Delta.StopReason
				}
			}
		case "gemini":
			var v struct {
				Candidates []struct {
					Content struct {
						Parts []struct {
							Text string `json:"text"`
						} `json:"parts"`
					} `json:"content"`
					FinishReason string `json:"finishReason"`
				} `json:"candidates"`
				UsageMetadata struct {
					PromptTokenCount     int `json:"promptTokenCount"`
					CandidatesTokenCount int `json:"candidatesTokenCount"`
					TotalTokenCount      int `json:"totalTokenCount"`
				} `json:"usageMetadata"`
			}
			if json.Unmarshal(data, &v) != nil {
				return
			}
			for _, c := range v.Candidates {
				for _, p := range c.Content.Parts {
					em.Delta(p.Text)
				}
				if c.FinishReason != "" {
					usage.Reason = c.FinishReason
				}
			}
			if v.UsageMetadata.TotalTokenCount > 0 {
				usage.Prompt = v.UsageMetadata.PromptTokenCount
				usage.Completion = v.UsageMetadata.CandidatesTokenCount
				usage.Total = v.UsageMetadata.TotalTokenCount
			}
		default:
			var v struct {
				Choices []struct {
					Delta struct {
						Content string `json:"content"`
					} `json:"delta"`
					FinishReason string `json:"finish_reason"`
				} `json:"choices"`
				Usage *struct {
					PromptTokens     int `json:"prompt_tokens"`
					CompletionTokens int `json:"completion_tokens"`
					TotalTokens      int `json:"total_tokens"`
				} `json:"usage"`
			}
			if json.Unmarshal(data, &v) != nil {
				return
			}
			for _, c := range v.Choices {
				if c.Delta.Content != "" {
					em.Delta(c.Delta.Content)
				}
				if c.FinishReason != "" {
					usage.Reason = c.FinishReason
				}
			}
			if v.Usage != nil {
				usage.Prompt = v.Usage.PromptTokens
				usage.Completion = v.Usage.CompletionTokens
				usage.Total = v.Usage.TotalTokens
			}
		}
	})
	em.End(usage)
	_ = err
	em.End(usage)
	// 已经向下游写了 200/SSE，不能再换账号重试（否则会向同一响应写第二份流）。
	return usage, true
}

func parseProviderResponse(typ string, raw []byte) canonicalResp {
	switch typ {
	case "anthropic":
		return parseAnthropicResponse(raw)
	case "gemini":
		return parseGeminiResponse(raw)
	default:
		return parseOpenAIResponse(raw)
	}
}

func buildAnthropicStreamRequest(c canonicalReq) []byte {
	raw := buildAnthropicRequest(c)
	var m map[string]interface{}
	if json.Unmarshal(raw, &m) != nil {
		return raw
	}
	m["stream"] = true
	out, _ := json.Marshal(m)
	return out
}

func readSSE(r io.Reader, fn func([]byte)) error {
	sc := bufio.NewScanner(r)
	sc.Buffer(make([]byte, 64<<10), 4<<20)
	for sc.Scan() {
		line := sc.Text()
		if !strings.HasPrefix(line, "data:") {
			continue
		}
		data := strings.TrimSpace(strings.TrimPrefix(line, "data:"))
		if data == "" || data == "[DONE]" {
			continue
		}
		fn([]byte(data))
	}
	return sc.Err()
}

func newEmitter(proto string) streamEmitter {
	switch proto {
	case "anthropic":
		return &anthropicEmitter{}
	case "gemini":
		return &geminiEmitter{}
	default:
		return &openAIEmitter{}
	}
}

type openAIEmitter struct{ w http.ResponseWriter }

func (e *openAIEmitter) Start(w http.ResponseWriter) {
	e.w = w
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")
	w.WriteHeader(http.StatusOK)
	chunk := map[string]interface{}{
		"id": "chatcmpl-accountpool", "object": "chat.completion.chunk",
		"created": model.Now(), "choices": []map[string]interface{}{{"index": 0, "delta": map[string]interface{}{"role": "assistant"}, "finish_reason": nil}},
	}
	raw, _ := json.Marshal(chunk)
	fmt.Fprintf(e.w, "data: %s\n\n", raw)
	flush(e.w)
}

func (e *openAIEmitter) Delta(text string) {
	if text == "" {
		return
	}
	chunk := map[string]interface{}{
		"id": "chatcmpl-accountpool", "object": "chat.completion.chunk",
		"created": model.Now(), "choices": []map[string]interface{}{{"index": 0, "delta": map[string]interface{}{"content": text}, "finish_reason": nil}},
	}
	raw, _ := json.Marshal(chunk)
	fmt.Fprintf(e.w, "data: %s\n\n", raw)
	flush(e.w)
}

func (e *openAIEmitter) End(u streamUsage) {
	reason := u.Reason
	if reason == "" {
		reason = "stop"
	}
	chunk := map[string]interface{}{
		"id": "chatcmpl-accountpool", "object": "chat.completion.chunk",
		"created": model.Now(), "choices": []map[string]interface{}{{"index": 0, "delta": map[string]interface{}{}, "finish_reason": reason}},
	}
	raw, _ := json.Marshal(chunk)
	fmt.Fprintf(e.w, "data: %s\n\n", raw)
	fmt.Fprint(e.w, "data: [DONE]\n\n")
	flush(e.w)
}

type anthropicEmitter struct {
	w       http.ResponseWriter
	started bool
}

func (e *anthropicEmitter) Start(w http.ResponseWriter) {
	e.w = w
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.WriteHeader(http.StatusOK)
	fmt.Fprint(e.w, "event: message_start\ndata: {\"type\":\"message_start\",\"message\":{\"id\":\"msg_accountpool\",\"type\":\"message\",\"role\":\"assistant\",\"content\":[],\"usage\":{\"input_tokens\":0,\"output_tokens\":0}}}\n\n")
	fmt.Fprint(e.w, "event: content_block_start\ndata: {\"type\":\"content_block_start\",\"index\":0,\"content_block\":{\"type\":\"text\",\"text\":\"\"}}\n\n")
	e.started = true
	flush(e.w)
}

func (e *anthropicEmitter) Delta(text string) {
	if text == "" {
		return
	}
	raw, _ := json.Marshal(map[string]interface{}{
		"type": "content_block_delta", "index": 0,
		"delta": map[string]interface{}{"type": "text_delta", "text": text},
	})
	fmt.Fprintf(e.w, "event: content_block_delta\ndata: %s\n\n", raw)
	flush(e.w)
}

func (e *anthropicEmitter) End(u streamUsage) {
	fmt.Fprint(e.w, "event: content_block_stop\ndata: {\"type\":\"content_block_stop\",\"index\":0}\n\n")
	reason := u.Reason
	if reason == "" {
		reason = "end_turn"
	}
	raw, _ := json.Marshal(map[string]interface{}{
		"type": "message_delta", "delta": map[string]interface{}{"stop_reason": reason},
		"usage": map[string]interface{}{"output_tokens": u.Completion},
	})
	fmt.Fprintf(e.w, "event: message_delta\ndata: %s\n\n", raw)
	fmt.Fprint(e.w, "event: message_stop\ndata: {\"type\":\"message_stop\"}\n\n")
	flush(e.w)
}

type geminiEmitter struct{ w http.ResponseWriter }

func (e *geminiEmitter) Start(w http.ResponseWriter) {
	e.w = w
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.WriteHeader(http.StatusOK)
	flush(e.w)
}

func (e *geminiEmitter) Delta(text string) {
	if text == "" {
		return
	}
	raw, _ := json.Marshal(map[string]interface{}{
		"candidates": []map[string]interface{}{{"content": map[string]interface{}{"role": "model", "parts": []map[string]interface{}{{"text": text}}}}},
	})
	fmt.Fprintf(e.w, "data: %s\n\n", raw)
	flush(e.w)
}

func (e *geminiEmitter) End(u streamUsage) {
	reason := u.Reason
	if reason == "" {
		reason = "STOP"
	}
	raw, _ := json.Marshal(map[string]interface{}{
		"candidates":    []map[string]interface{}{{"content": map[string]interface{}{"role": "model", "parts": []map[string]interface{}{}}, "finishReason": reason}},
		"usageMetadata": map[string]interface{}{"promptTokenCount": u.Prompt, "candidatesTokenCount": u.Completion, "totalTokenCount": u.Total},
	})
	fmt.Fprintf(e.w, "data: %s\n\n", raw)
	flush(e.w)
}

func flush(w http.ResponseWriter) {
	if f, ok := w.(http.Flusher); ok {
		f.Flush()
	}
}
