export function buildSystemPrompt(base, skills) {
    const list = (skills || []).filter((s) => s && s.instructions);
    if (!list.length)
        return base;
    const parts = list.map((s) => `## Skill: ${s.title}\n${s.instructions.trim()}`);
    return base + '\n\n--- 已启用的技能 ---\n' + parts.join('\n\n');
}
