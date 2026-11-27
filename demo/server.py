#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""demo 插件后端(接口库 v4): 经 rcplugin SDK 自注册 + 接口实现。

独立进程, 无端口; 端点在 <插件目录>/.rc.endpoint(主系统预写)。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rcplugin as rc


@rc.interface("demo.ping")
def demo_ping(params):
    return {"pong": True, "plugin": "demo", "params": params}


@rc.interface("demo.echo")
def demo_echo(params):
    return {"echo": params}


@rc.interface("demo.cross")
def demo_cross(params):
    # 跨接口调用: 经主系统接口库路由回本插件 echo(演示总线)
    return {"self_call": rc.call("demo.echo", {"from": "demo.cross", **params})}


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    rc.serve(
        endpoint=os.environ.get("RC_ENDPOINT", ""),
        name="demo",
        version="1.0.0",
        manifest={"label": "接口演示", "description": "v4 最小演示"},
        frontend={"pages": [{"path": "", "title": "接口演示"}]},
        iface_ids=["demo.ping", "demo.echo", "demo.cross"],
        plugin_dir=here,
    )