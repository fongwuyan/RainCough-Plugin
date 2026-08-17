function buildMessages(model, msgs) {
    const isDeepseek = model.toLowerCase().includes('deepseek');
    const out = [];
    for (const m of msgs) {
        switch (m.role) {
            case 'system':
            case 'user':
                out.push({ role: m.role, content: m.content });
                break;
            case 'tool':
                out.push({ role: 'tool', tool_call_id: m.tool_call_id, content: m.content });
                break;
            case 'assistant': {
                const a = { role: 'assistant', content: m.content || '' };
                if (m.tool_calls && m.tool_calls.length) {
                    a.tool_calls = m.tool_calls.map((t) => ({
                        id: t.id,
                        type: 'function',
                        function: { name: t.name, arguments: t.arguments },
                    }));
                }
                if (isDeepseek && m.reasoning_content)
                    a.reasoning_content = m.reasoning_content;
                out.push(a);
                break;
            }
        }
    }
    return out;
}
export async function streamChat(cfg, messages, tools, h) {
    const base = cfg.api_base.replace(/\/+$/, '');
    const body = {
        model: cfg.model,
        messages: buildMessages(cfg.model, messages),
        stream: true,
        temperature: 0.2,
        max_tokens: 8192,
    };
    if (tools && tools.length)
        body.tools = tools;
    const res = await fetch(base + '/chat/completions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: 'Bearer ' + cfg.api_key,
        },
        body: JSON.stringify(body),
    });
    if (!res.ok) {
        let txt = '';
        try {
            txt = (await res.text()).slice(0, 400);
        }
        catch { }
        throw new Error(`LLM 请求失败 HTTP ${res.status}: ${txt}`);
    }
    if (!res.body)
        throw new Error('LLM 无响应体');
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buf = '';
    const acc = [];
    const result = { content: '', reasoning_content: '', tool_calls: [] };
    for (;;) {
        const { done, value } = await reader.read();
        if (done)
            break;
        buf += decoder.decode(value, { stream: true });
        let idx;
        while ((idx = buf.indexOf('\n')) >= 0) {
            const line = buf.slice(0, idx).trim();
            buf = buf.slice(idx + 1);
            if (!line.startsWith('data:'))
                continue;
            const data = line.slice(5).trim();
            if (!data || data === '[DONE]')
                continue;
            let j;
            try {
                j = JSON.parse(data);
            }
            catch {
                continue;
            }
            const choice = j.choices && j.choices[0];
            if (!choice)
                continue;
            const d = choice.delta || {};
            if (typeof d.content === 'string' && d.content) {
                result.content += d.content;
                if (h.onContent)
                    h.onContent(d.content);
            }
            if (typeof d.reasoning_content === 'string' && d.reasoning_content) {
                result.reasoning_content += d.reasoning_content;
                if (h.onReasoning)
                    h.onReasoning(d.reasoning_content);
            }
            if (Array.isArray(d.tool_calls)) {
                for (const tc of d.tool_calls) {
                    if (!tc || typeof tc !== 'object')
                        continue;
                    const cur = acc[tc.index] || (acc[tc.index] = { index: tc.index, id: '', name: '', arguments: '' });
                    if (typeof tc.id === 'string' && tc.id)
                        cur.id = tc.id;
                    if (tc.function) {
                        if (typeof tc.function.name === 'string')
                            cur.name += tc.function.name;
                        if (typeof tc.function.arguments === 'string')
                            cur.arguments += tc.function.arguments;
                    }
                }
            }
        }
    }
    result.tool_calls = acc
        .filter(Boolean)
        .map((t) => ({
        id: t.id || 'call_' + Math.random().toString(36).slice(2, 10),
        name: t.name,
        arguments: t.arguments,
    }));
    return result;
}
