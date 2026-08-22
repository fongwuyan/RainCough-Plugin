/**
 * 系统消息内容 = 用户自定义工作原则 + 长期记忆。
 * 不叠加任何品牌/人格/固定行为引导。
 */
export function buildSystemPrompt(principles, memory = '') {
    const parts = [];
    const ps = (principles || []).map((p) => String(p).trim()).filter(Boolean);
    if (ps.length) {
        parts.push(ps.join('\n'));
    }
    if (memory && memory.trim()) {
        parts.push('--- 长期记忆 ---\n' + memory.trim());
    }
    return parts.join('\n\n');
}
/** 供 tools.ts 引用 Skill 类型数组, 避免未使用告警 */
export function sanitizeSkills(raw) {
    if (!Array.isArray(raw))
        return [];
    return raw
        .filter((s) => s && typeof s === 'object' && typeof s.name === 'string')
        .map((s) => ({
        name: String(s.name || 'skill'),
        title: String(s.title || s.name || 'skill'),
        description: String(s.description || ''),
        enabled: s.enabled !== false,
        params: Array.isArray(s.params) ? s.params : [],
        execution: (s.execution && { kind: 'shell', command: '', ...s.execution }) || { kind: 'shell', command: '' },
        builtin: !!s.builtin,
    }));
}
