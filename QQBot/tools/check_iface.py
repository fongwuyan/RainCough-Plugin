# -*- coding: utf-8 -*-
"""前后端接口一致性检查。

前端调用的接口如果后端没有 → 运行时 404（面板对"接口不存在"返回 404），
页面表现是某个功能静默失效（比如运行日志页一直报 "invoke failed"）。

★ 这个 bug 我踩过：单账户重构删了 qqbot.nc.logs，
  前端还在调 → 日志页坏了但没人发现。
  所以这个检查应该在提交前跑。

用法: python3 tools/check_iface.py
"""
import re
import sys

FRONT = 'frontend/plugin.js'
BACK = 'server_v4.py'

# 前端用的这些是宿主提供的，不在插件后端里
HOST_OK = set()


def main():
    front = open(FRONT, encoding='utf-8').read()
    back = open(BACK, encoding='utf-8').read()

    used = set(re.findall(r"call(?:Data)?\('([a-z_.]+)'", front))

    # 后端注册的：@rc.interface("xxx") 和 IFACES 清单
    reg = set(re.findall(r'@rc\.interface\("([a-z_.]+)"\)', back))
    listed = set(re.findall(r'"((?:qqbot|rcbot)\.[a-z_.]+)"', back))

    missing = sorted(used - reg - listed - HOST_OK)
    # 反向：清单里声明了但没有实现（面板会报接口不存在）
    ghost = sorted((listed - reg) & set())

    print('前端调用 %d 个接口' % len(used))
    print('后端实现 %d 个' % len(reg))
    if missing:
        print('\n!! 前端调了但后端没有实现:')
        for m in missing:
            print('   %s' % m)
    if ghost:
        print('\n!! 清单里声明了但没有实现:')
        for g in ghost:
            print('   %s' % g)
    if not missing and not ghost:
        print('\n一致 OK')
        return 0
    return 1


if __name__ == '__main__':
    sys.exit(main())
