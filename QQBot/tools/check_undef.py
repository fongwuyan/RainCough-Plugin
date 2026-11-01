#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""静态检查：找函数里"引用了但没定义"的变量。

★ 为什么要自己写：ast.parse 只查语法，查不出 NameError。
  这次就因为把 webui_port 改名却漏改下面的引用（wp），
  导致整个概览接口抛 "name 'wp' is not defined" —— 页面直接空白。

用法:
    python3 tools/check_undef.py server_v4.py [rcbot/*.py]
"""
import builtins
import os
import sys


def check(path):
    src = open(path, encoding='utf-8').read()
    tree = compile(src, path, 'exec', flags=0, dont_inherit=True)  # 语法校验

    import ast
    t = ast.parse(src)

    # 全局作用域收集的定义
    # ★ 只收"真正的全局绑定"：模块级语句里的 def/class/import/赋值。
    #   不能把嵌套函数里的赋值也算进来 —— 那样任何变量都会被当成全局，
    #   检查就形同虚设（实测：函数内用到的 wp 被别处的同名赋值"洗白"了）。
    globals_ = set(dir(builtins))
    for node in t.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            globals_.add(node.name)
        elif isinstance(node, ast.Assign):
            for tgt in node.targets:
                for sub in ast.walk(tgt):
                    if isinstance(sub, ast.Name):
                        globals_.add(sub.id)
        elif isinstance(node, ast.AnnAssign) and node.target:
            for sub in ast.walk(node.target):
                if isinstance(sub, ast.Name):
                    globals_.add(sub.id)
        elif isinstance(node, ast.AugAssign) and node.target:
            for sub in ast.walk(node.target):
                if isinstance(sub, ast.Name):
                    globals_.add(sub.id)
        elif isinstance(node, ast.Import):
            for a in node.names:
                globals_.add((a.asname or a.name).split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            for a in node.names:
                globals_.add(a.asname or a.name)
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            for sub in ast.walk(node.target):
                if isinstance(sub, ast.Name):
                    globals_.add(sub.id)
        elif isinstance(node, ast.withitem) and node.optional_vars:
            for sub in ast.walk(node.optional_vars):
                if isinstance(sub, ast.Name):
                    globals_.add(sub.id)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            globals_.add(node.name)

    problems = []

    def visit_fn(fn, outer):
        # 函数内定义的（含嵌套）
        local = set()
        for a in ast.walk(fn):
            if isinstance(a, ast.Name) and isinstance(a.ctx, ast.Store):
                local.add(a.id)
            elif isinstance(a, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                local.add(a.name)
            elif isinstance(a, ast.Import):
                for al in a.names:
                    local.add((al.asname or al.name).split('.')[0])
            elif isinstance(a, ast.ImportFrom):
                for al in a.names:
                    local.add(al.asname or al.name)
            elif isinstance(a, ast.arg):
                local.add(a.arg)
            elif isinstance(a, ast.ExceptHandler) and a.name:
                local.add(a.name)
            elif isinstance(a, ast.Global) or isinstance(a, ast.Nonlocal):
                for nm in a.names:
                    local.add(nm)

        # 被引用但既不在 local 也不在 globals_ → 可疑
        used = {}
        for a in ast.walk(fn):
            if isinstance(a, ast.Name) and isinstance(a.ctx, ast.Load):
                used.setdefault(a.id, a.lineno)

        for name, line in sorted(used.items()):
            if name in local or name in globals_ or name in outer:
                continue
            # 嵌套函数引用外层变量是合法的
            if name in outer:
                continue
            problems.append('%s:%d  未定义变量 %r' % (path, line, name))

    def walk(node, outer):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                local = set(outer)
                visit_fn(child, local)
                walk(child, local)
            elif isinstance(child, ast.ClassDef):
                walk(child, outer)
            else:
                walk(child, outer)

    walk(t, set())
    return problems


def main():
    files = sys.argv[1:] or ['server_v4.py']
    bad = 0
    for f in files:
        if not os.path.isfile(f):
            continue
        try:
            ps = check(f)
        except SyntaxError as e:
            print('%s: 语法错误 %s' % (f, e))
            bad += 1
            continue
        for p in ps:
            print(p)
            bad += 1
    if not bad:
        print('检查通过：没有发现未定义变量')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
