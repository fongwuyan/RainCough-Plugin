# -*- coding: utf-8 -*-
"""rcbot —— RainCough 自研 QQ 机器人核心。

只做五件事：模型提供商、人格、会话管理、上下文压缩、运行日志。
QQ 收发走 NapCat 的 OneBot 11 正向 WS（默认 ws://127.0.0.1:6700）。
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aiohttp import web  # noqa: E402

from rcbot import api, bot as botmod, config, logbuf, onebot, store  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))


async def main():
    logbuf.setup(os.path.join(ROOT, 'logs', 'rcbot.log'),
                 os.environ.get('RCBOT_LOG_LEVEL', 'INFO'))
    logbuf.info('main', 'rcbot 启动')

    cfg = config.load()
    await store.init()

    ob = onebot.OneBot(config.load, None)
    b = botmod.Bot(ob)
    ob.on_event = b.on_event

    asyncio.create_task(ob.run())

    async def warm():
        """连上后补一次群名，失败就算了。"""
        for _ in range(60):
            await asyncio.sleep(2)
            if ob.connected:
                await asyncio.sleep(1)
                await b.fill_group_names()
                return

    asyncio.create_task(warm())

    app = api.make_app(ob, b)
    runner = web.AppRunner(app)
    await runner.setup()
    host = (cfg.get('http') or {}).get('host') or '127.0.0.1'
    port = int((cfg.get('http') or {}).get('port') or 6710)
    site = web.TCPSite(runner, host, port)
    await site.start()
    logbuf.info('main', 'HTTP API 监听 http://%s:%d' % (host, port))

    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()
        await store.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
