# -*- coding: utf-8 -*-
"""QQ 头像与昵称解析。

★ 为什么要单独一个模块：
  头像/昵称在三个地方都要用 —— 概览的账号卡片、QQ 账户列表、聊天记录里的
  发言者。之前每一处各自拼、各自取，结果是：
    · 概览只从 GetQuickLoginListNew 取（已登录才有），
      没登录就全空，界面上一片灰圆圈；
    · 聊天记录里的发言者根本没有头像字段，
      前端只能显示一个空白 div。

★ 头像从哪来：
  OneBot 的 get_login_info 只返回 {user_id, nickname}，**没有头像**；
  群成员信息（get_group_member_info）也没有。
  QQ 头像本身是独立服务，按 QQ 号就能取：
      https://q1.qlogo.cn/g?b=qq&nk=<QQ号>&s=<边长>
  实测 200 + image/jpeg，可以直接放进 <img src>。
  所以头像不需要等 QQ 登录，只要知道 QQ 号就能显示。

★ 昵称优先级：
  群名片(card) > 昵称(nickname) > QQ 号
  —— 群里别人看到的名字通常是群名片。
"""

# 头像服务。q1/q2 是腾讯的 CDN，任选其一都能取到。
_AVA_HOSTS = ('https://q1.qlogo.cn', 'https://q2.qlogo.cn')


def avatar_url(uin, size=100):
    """按 QQ 号拼头像 URL。QQ 号无效时返回空串。

    size 是方形边长（像素），腾讯支持 40/100/240 等。
    """
    u = str(uin or '').strip()
    if not u.isdigit():
        return ''
    if len(u) < 5 or len(u) > 12:
        return ''
    return '%s/g?b=qq&nk=%s&s=%d' % (_AVA_HOSTS[0], u, int(size))


def display_name(uin, nick='', card=''):
    """显示名：群名片 > 昵称 > QQ 号。

    card 是群里的名片（sender.card），nick 是个人昵称（sender.nickname）。
    """
    for v in (card, nick):
        s = str(v or '').strip()
        if s:
            return s
    return str(uin or '')


def sender_profile(sender):
    """从 OneBot 事件里的 sender 提取 (uin, name, avatar)。

    sender 结构（OneBot11）：
        {user_id, nickname, card, role, sex, age, title, level}
    群名片在 card，个人昵称在 nickname。
    """
    s = sender or {}
    uin = str(s.get('user_id') or s.get('uin') or '').strip()
    name = display_name(uin, s.get('nickname') or '', s.get('card') or '')
    return uin, name, avatar_url(uin)
