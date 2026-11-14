package server

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"

	"accountpool/internal/model"
	"accountpool/internal/pool"
)

type canonicalMsg struct {
	Role    string
	Content string
}

type canonicalReq struct {
	Model       string
	System      string
	Messages    []canonicalMsg
	MaxTokens   int
	Temperature *float64
	Stream      bool
}

type canonicalResp struct {
	Text             string
	PromptTokens     int
	CompletionTokens int
	TotalTokens      int
	FinishReason     string
}

func parseOpenAIRequest(body []byte) (canonicalReq, error) {
	var v struct {
		Model       string            `json:"model"`
		Messages    []json.RawMessage `json:"messages"`
		MaxTokens   int               `json:"max_tokens"`
		Temperature *float64          `json:"temperature"`
		Stream      bool              `json:"stream"`
	}
	if err := json.Unmarshal(body, &v); err != nil {
		return canonicalReq{}, err
	}
	if v.Model == "" {
		return canonicalReq{}, fmt.Errorf("model 必填")
	}
	out := canonicalReq{Model: v.Model, MaxTokens: v.MaxTokens, Temperature: v.Temperature, Stream: v.Stream}
	for _, raw := range v.Messages {
		var m struct {
			Role    string          `json:"role"`
			Content json.RawMessage `json:"content"`
		}
		if json.Unmarshal(raw, &m) != nil {
			continue
		}
		text := contentText(m.Content)
		if m.Role == "system" {
			if out.System != "" {
				out.System += "\n"
			}
			out.System += text
			continue
		}
		out.Messages = append(out.Messages, canonicalMsg{Role: m.Role, Content: text})
	}
	if len(out.Messages) == 0 {
		return canonicalReq{}, fmt.Errorf("messages 必填")
	}
	return out, nil
}

func parseAnthropicRequest(body []byte) (canonicalReq, error) {
	var v struct {
		Model    string          `json:"model"`
		System   json.RawMessage `json:"system"`
		Messages []struct {
			Role    string          `json:"role"`
			Content json.RawMessage `json:"content"`
		} `json:"messages"`
		MaxTokens   int      `json:"max_tokens"`
		Temperature *float64 `json:"temperature"`
		Stream      bool     `json:"stream"`
	}
	if err := json.Unmarshal(body, &v); err != nil {
		return canonicalReq{}, err
	}
	if v.Model == "" {
		return canonicalReq{}, fmt.Errorf("model 必填")
	}
	out := canonicalReq{Model: v.Model, System: contentText(v.System), MaxTokens: v.MaxTokens, Temperature: v.Temperature, Stream: v.Stream}
	for _, m := range v.Messages {
		out.Messages = append(out.Messages, canonicalMsg{Role: m.Role, Content: contentText(m.Content)})
	}
	return out, nil
}

func parseGeminiRequest(body []byte) (canonicalReq, error) {
	var v struct {
		SystemInstruction *struct {
			Parts []struct {
				Text string `json:"text"`
			} `json:"parts"`
		} `json:"systemInstruction"`
		Contents []struct {
			Role  string `json:"role"`
			Parts []struct {
				Text string `json:"text"`
			} `json:"parts"`
		} `json:"contents"`
		GenerationConfig struct {
			MaxOutputTokens int      `json:"maxOutputTokens"`
			Temperature     *float64 `json:"temperature"`
		} `json:"generationConfig"`
	}
	if err := json.Unmarshal(body, &v); err != nil {
		return canonicalReq{}, err
	}
	out := canonicalReq{MaxTokens: v.GenerationConfig.MaxOutputTokens, Temperature: v.GenerationConfig.Temperature}
	if v.SystemInstruction != nil {
		for _, p := range v.SystemInstruction.Parts {
			out.System += p.Text
		}
	}
	for _, c := range v.Contents {
		role := c.Role
		if role == "model" {
			role = "assistant"
		}
		var text strings.Builder
		for _, p := range c.Parts {
			text.WriteString(p.Text)
		}
		out.Messages = append(out.Messages, canonicalMsg{Role: role, Content: text.String()})
	}
	return out, nil
}

func contentText(raw json.RawMessage) string {
	if len(raw) == 0 {
		return ""
	}
	var s string
	if json.Unmarshal(raw, &s) == nil {
		return s
	}
	var blocks []struct {
		Type string `json:"type"`
		Text string `json:"text"`
	}
	if json.Unmarshal(raw, &blocks) == nil {
		var b strings.Builder
		for _, x := range blocks {
			if x.Text != "" {
				b.WriteString(x.Text)
			}
		}
		return b.String()
	}
	var obj struct {
		Text string `json:"text"`
	}
	_ = json.Unmarshal(raw, &obj)
	return obj.Text
}

func buildOpenAIRequest(c canonicalReq, stream bool) []byte {
	msgs := make([]map[string]interface{}, 0, len(c.Messages)+1)
	if c.System != "" {
		msgs = append(msgs, map[string]interface{}{"role": "system", "content": c.System})
	}
	for _, m := range c.Messages {
		msgs = append(msgs, map[string]interface{}{"role": m.Role, "content": m.Content})
	}
	body := map[string]interface{}{"model": c.Model, "messages": msgs, "stream": stream}
	if c.MaxTokens > 0 {
		body["max_tokens"] = c.MaxTokens
	}
	if c.Temperature != nil {
		body["temperature"] = *c.Temperature
	}
	raw, _ := json.Marshal(body)
	return raw
}

func buildAnthropicRequest(c canonicalReq) []byte {
	msgs := make([]map[string]interface{}, 0, len(c.Messages))
	for _, m := range c.Messages {
		msgs = append(msgs, map[string]interface{}{"role": m.Role, "content": m.Content})
	}
	body := map[string]interface{}{"model": c.Model, "messages": msgs, "stream": false}
	if c.System != "" {
		body["system"] = c.System
	}
	max := c.MaxTokens
	if max <= 0 {
		max = 4096
	}
	body["max_tokens"] = max
	if c.Temperature != nil {
		body["temperature"] = *c.Temperature
	}
	raw, _ := json.Marshal(body)
	return raw
}

func buildGeminiRequest(c canonicalReq) []byte {
	contents := make([]map[string]interface{}, 0, len(c.Messages))
	for _, m := range c.Messages {
		role := m.Role
		if role == "assistant" {
			role = "model"
		}
		contents = append(contents, map[string]interface{}{
			"role": role, "parts": []map[string]interface{}{{"text": m.Content}},
		})
	}
	body := map[string]interface{}{"contents": contents}
	if c.System != "" {
		body["systemInstruction"] = map[string]interface{}{
			"parts": []map[string]interface{}{{"text": c.System}},
		}
	}
	gen := map[string]interface{}{}
	if c.MaxTokens > 0 {
		gen["maxOutputTokens"] = c.MaxTokens
	}
	if c.Temperature != nil {
		gen["temperature"] = *c.Temperature
	}
	if len(gen) > 0 {
		body["generationConfig"] = gen
	}
	raw, _ := json.Marshal(body)
	return raw
}

func parseOpenAIResponse(raw []byte) canonicalResp {
	var v struct {
		Choices []struct {
			Message struct {
				Content string `json:"content"`
			} `json:"message"`
			FinishReason string `json:"finish_reason"`
		} `json:"choices"`
		Usage struct {
			PromptTokens     int `json:"prompt_tokens"`
			CompletionTokens int `json:"completion_tokens"`
			TotalTokens      int `json:"total_tokens"`
		} `json:"usage"`
	}
	if json.Unmarshal(raw, &v) != nil {
		return canonicalResp{}
	}
	out := canonicalResp{PromptTokens: v.Usage.PromptTokens, CompletionTokens: v.Usage.CompletionTokens, TotalTokens: v.Usage.TotalTokens}
	if len(v.Choices) > 0 {
		out.Text = v.Choices[0].Message.Content
		out.FinishReason = v.Choices[0].FinishReason
	}
	return out
}

func parseAnthropicResponse(raw []byte) canonicalResp {
	var v struct {
		Content []struct {
			Type string `json:"type"`
			Text string `json:"text"`
		} `json:"content"`
		StopReason string `json:"stop_reason"`
		Usage      struct {
			InputTokens  int `json:"input_tokens"`
			OutputTokens int `json:"output_tokens"`
		} `json:"usage"`
	}
	if json.Unmarshal(raw, &v) != nil {
		return canonicalResp{}
	}
	var b strings.Builder
	for _, c := range v.Content {
		if c.Type == "text" {
			b.WriteString(c.Text)
		}
	}
	return canonicalResp{
		Text: b.String(), PromptTokens: v.Usage.InputTokens,
		CompletionTokens: v.Usage.OutputTokens,
		TotalTokens:      v.Usage.InputTokens + v.Usage.OutputTokens,
		FinishReason:     v.StopReason,
	}
}

func parseGeminiResponse(raw []byte) canonicalResp {
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
	if json.Unmarshal(raw, &v) != nil {
		return canonicalResp{}
	}
	var b strings.Builder
	if len(v.Candidates) > 0 {
		for _, p := range v.Candidates[0].Content.Parts {
			b.WriteString(p.Text)
		}
	}
	finish := ""
	if len(v.Candidates) > 0 {
		finish = v.Candidates[0].FinishReason
	}
	return canonicalResp{
		Text: b.String(), PromptTokens: v.UsageMetadata.PromptTokenCount,
		CompletionTokens: v.UsageMetadata.CandidatesTokenCount,
		TotalTokens:      v.UsageMetadata.TotalTokenCount,
		FinishReason:     finish,
	}
}

func buildOpenAIResponse(c canonicalResp, modelName string) []byte {
	reason := c.FinishReason
	if reason == "" {
		reason = "stop"
	}
	body := map[string]interface{}{
		"id": "chatcmpl-accountpool", "object": "chat.completion", "created": model.Now(),
		"model": modelName,
		"choices": []map[string]interface{}{{
			"index": 0, "message": map[string]interface{}{"role": "assistant", "content": c.Text},
			"finish_reason": reason,
		}},
		"usage": map[string]interface{}{"prompt_tokens": c.PromptTokens, "completion_tokens": c.CompletionTokens, "total_tokens": c.TotalTokens},
	}
	raw, _ := json.Marshal(body)
	return raw
}

func buildAnthropicResponse(c canonicalResp) []byte {
	body := map[string]interface{}{
		"id": "msg_accountpool", "type": "message", "role": "assistant",
		"content":     []map[string]interface{}{{"type": "text", "text": c.Text}},
		"stop_reason": c.FinishReason,
		"usage":       map[string]interface{}{"input_tokens": c.PromptTokens, "output_tokens": c.CompletionTokens},
	}
	raw, _ := json.Marshal(body)
	return raw
}

func buildGeminiResponse(c canonicalResp) []byte {
	body := map[string]interface{}{
		"candidates": []map[string]interface{}{{
			"content":      map[string]interface{}{"role": "model", "parts": []map[string]interface{}{{"text": c.Text}}},
			"finishReason": c.FinishReason,
		}},
		"usageMetadata": map[string]interface{}{
			"promptTokenCount": c.PromptTokens, "candidatesTokenCount": c.CompletionTokens,
			"totalTokenCount": c.TotalTokens,
		},
	}
	raw, _ := json.Marshal(body)
	return raw
}

// crossServe 处理“下游协议与上游 Provider 不同”的请求。
// 当前跨协议流式采用缓冲后一次下发，保证客户端协议兼容；真流式在后续版本补齐。
func (s *Server) crossServe(w http.ResponseWriter, r *http.Request, body []byte, proto, modelName string,
	tok *model.Token, start time.Time) bool {
	var req canonicalReq
	var err error
	switch proto {
	case "openai":
		req, err = parseOpenAIRequest(body)
	case "anthropic":
		req, err = parseAnthropicRequest(body)
	case "gemini":
		req, err = parseGeminiRequest(body)
	}
	if err != nil {
		return false
	}
	req.Model = modelName
	if req.Model == "" {
		return false
	}
	failed := map[string]bool{}
	for attempt := 0; attempt < 3; attempt++ {
		sel, err := s.Pool.Select(req.Model, failed)
		if err != nil {
			return false
		}
		resp, ok := s.callCanonical(sel, req)
		s.Pool.Release(sel.Account.ID)
		if !ok {
			failed[sel.Account.ID] = true
			continue
		}
		switch proto {
		case "openai":
			if req.Stream {
				writeOpenAIStream(w, resp, req.Model)
			} else {
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(http.StatusOK)
				_, _ = w.Write(buildOpenAIResponse(resp, req.Model))
			}
		case "anthropic":
			if req.Stream {
				writeAnthropicStream(w, resp)
			} else {
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(http.StatusOK)
				_, _ = w.Write(buildAnthropicResponse(resp))
			}
		case "gemini":
			if req.Stream {
				writeGeminiStream(w, resp)
			} else {
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(http.StatusOK)
				_, _ = w.Write(buildGeminiResponse(resp))
			}
		}
		s.Pool.MarkOK(sel.Account.ID)
		s.recordUsage(tok.ID, sel, req.Model, resp.PromptTokens, resp.CompletionTokens, resp.TotalTokens,
			time.Since(start).Milliseconds(), 200, "")
		return true
	}
	return false
}

func (s *Server) callCanonical(sel *pool.Selection, req canonicalReq) (canonicalResp, bool) {
	var url string
	var body []byte
	var headers map[string]string
	switch sel.Provider.Type {
	case "anthropic":
		url = anthropicMessagesURL(sel.Provider.BaseURL)
		body = buildAnthropicRequest(req)
		headers = map[string]string{"x-api-key": sel.Key, "anthropic-version": "2023-06-01"}
	case "gemini":
		url = geminiURL(sel.Provider.BaseURL, "models/"+req.Model+":generateContent", sel.Key, false)
		body = buildGeminiRequest(req)
	default:
		url = chatURL(sel.Provider.BaseURL)
		if sel.Provider.Type == "azure" {
			url = strings.TrimRight(sel.Provider.BaseURL, "/") + "/chat/completions?api-version=2024-10-21"
			headers = map[string]string{"api-key": sel.Key}
		} else {
			headers = map[string]string{"Authorization": "Bearer " + sel.Key}
		}
		body = buildOpenAIRequest(req, false)
	}
	httpReq, err := http.NewRequest(http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		s.Pool.Cooldown(sel.Account.ID, 30, err.Error())
		return canonicalResp{}, false
	}
	httpReq.Header.Set("Content-Type", "application/json")
	for k, v := range headers {
		httpReq.Header.Set(k, v)
	}
	resp, err := s.Client.Do(httpReq)
	if err != nil {
		s.Pool.Cooldown(sel.Account.ID, 60, trimErr(err.Error()))
		return canonicalResp{}, false
	}
	defer resp.Body.Close()
	raw, _ := io.ReadAll(io.LimitReader(resp.Body, 32<<20))
	if resp.StatusCode >= 400 {
		s.Pool.Cooldown(sel.Account.ID, nativeCooldown(resp.StatusCode), "HTTP "+fmt.Sprint(resp.StatusCode))
		return canonicalResp{}, false
	}
	switch sel.Provider.Type {
	case "anthropic":
		return parseAnthropicResponse(raw), true
	case "gemini":
		return parseGeminiResponse(raw), true
	default:
		return parseOpenAIResponse(raw), true
	}
}

func writeOpenAIStream(w http.ResponseWriter, c canonicalResp, modelName string) {
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.WriteHeader(http.StatusOK)
	chunk := map[string]interface{}{
		"id": "chatcmpl-accountpool", "object": "chat.completion.chunk", "created": model.Now(), "model": modelName,
		"choices": []map[string]interface{}{{"index": 0, "delta": map[string]interface{}{"role": "assistant", "content": c.Text}, "finish_reason": nil}},
	}
	raw, _ := json.Marshal(chunk)
	fmt.Fprintf(w, "data: %s\n\n", raw)
	fmt.Fprint(w, "data: [DONE]\n\n")
}

func writeAnthropicStream(w http.ResponseWriter, c canonicalResp) {
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.WriteHeader(http.StatusOK)
	fmt.Fprint(w, "event: message_start\ndata: {\"type\":\"message_start\",\"message\":{\"id\":\"msg_accountpool\",\"type\":\"message\",\"role\":\"assistant\",\"content\":[],\"usage\":{\"input_tokens\":"+fmt.Sprint(c.PromptTokens)+",\"output_tokens\":0}}}\n\n")
	fmt.Fprint(w, "event: content_block_start\ndata: {\"type\":\"content_block_start\",\"index\":0,\"content_block\":{\"type\":\"text\",\"text\":\"\"}}\n\n")
	raw, _ := json.Marshal(map[string]interface{}{"type": "content_block_delta", "index": 0, "delta": map[string]interface{}{"type": "text_delta", "text": c.Text}})
	fmt.Fprintf(w, "event: content_block_delta\ndata: %s\n\n", raw)
	fmt.Fprint(w, "event: content_block_stop\ndata: {\"type\":\"content_block_stop\",\"index\":0}\n\n")
	fmt.Fprintf(w, "event: message_delta\ndata: {\"type\":\"message_delta\",\"delta\":{\"stop_reason\":%q},\"usage\":{\"output_tokens\":%d}}\n\n", c.FinishReason, c.CompletionTokens)
	fmt.Fprint(w, "event: message_stop\ndata: {\"type\":\"message_stop\"}\n\n")
}

func writeGeminiStream(w http.ResponseWriter, c canonicalResp) {
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.WriteHeader(http.StatusOK)
	raw := buildGeminiResponse(c)
	fmt.Fprintf(w, "data: %s\n\n", raw)
}
