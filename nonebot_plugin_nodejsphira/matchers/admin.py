from nonebot import on_command, get_driver
from nonebot.adapters.qq import Message, Bot, Event
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import get_plugin_config
from datetime import datetime

from ..config import Config
from ..utils.api import admin_request

plugin_config = get_plugin_config(Config)

async def req(method: str, endpoint: str, json_data=None):
    return await admin_request(
        base_url=plugin_config.phira_api_url,
        secret=plugin_config.phira_admin_secret,
        method=method,
        endpoint=endpoint,
        json_data=json_data
    )

# 1. 玩家列表
players_cmd = on_command("players", priority=5, permission=SUPERUSER, block=True)
@players_cmd.handle()
async def _():
    data = await req("GET", "/api/all-players")
    if isinstance(data, dict) and "error" in data:
        await players_cmd.finish(f"失败: {data['error']}")
    
    if not data:
        await players_cmd.finish("无在线玩家")
    
    msg = ["当前在线:"]
    for p in data:
        msg.append(f"- {p.get('name')} ({p.get('id')}) Room:{p.get('roomId')}")
    await players_cmd.finish("\n".join(msg))

# 2. 广播
broadcast_cmd = on_command("broadcast", priority=5, permission=SUPERUSER, block=True)
@broadcast_cmd.handle()
async def _(args: Message = CommandArg()):
    txt = args.extract_plain_text().strip()
    if not txt: await broadcast_cmd.finish("用法: /broadcast 内容 [#target]")
    
    parts = txt.split(maxsplit=1)
    payload = {"content": parts[0].strip('"')}
    if len(parts) > 1: payload["target"] = parts[1]
    
    res = await req("POST", "/api/admin/broadcast", payload)
    await broadcast_cmd.finish(f"结果: {res}")

# 3. 踢人
kick_cmd = on_command("kick", priority=5, permission=SUPERUSER, block=True)
@kick_cmd.handle()
async def _(args: Message = CommandArg()):
    uid = args.extract_plain_text().strip()
    if not uid.isdigit(): await kick_cmd.finish("用法: /kick ID")
    res = await req("POST", "/api/admin/kick-player", {"userId": int(uid)})
    await kick_cmd.finish(f"结果: {res}")

# 4. 强制开始
fstart_cmd = on_command("fstart", priority=5, permission=SUPERUSER, block=True)
@fstart_cmd.handle()
async def _(args: Message = CommandArg()):
    rid = args.extract_plain_text().strip()
    res = await req("POST", "/api/admin/force-start", {"roomId": rid})
    await fstart_cmd.finish(f"结果: {res}")

# 5. 锁定
lock_cmd = on_command("lock", priority=5, permission=SUPERUSER, block=True)
@lock_cmd.handle()
async def _(args: Message = CommandArg()):
    rid = args.extract_plain_text().strip()
    res = await req("POST", "/api/admin/toggle-lock", {"roomId": rid})
    await lock_cmd.finish(f"结果: {res}")

# 6. 人数上限
maxp_cmd = on_command("maxp", priority=5, permission=SUPERUSER, block=True)
@maxp_cmd.handle()
async def _(args: Message = CommandArg()):
    txt = args.extract_plain_text().strip().split()
    if len(txt) < 2: await maxp_cmd.finish("用法: /maxp ID Num")
    res = await req("POST", "/api/admin/set-max-players", {"roomId": txt[0], "maxPlayers": int(txt[1])})
    await maxp_cmd.finish(f"结果: {res}")

# 7. 关闭房间
close_cmd = on_command("close", priority=5, permission=SUPERUSER, block=True)
@close_cmd.handle()
async def _(args: Message = CommandArg()):
    rid = args.extract_plain_text().strip()
    res = await req("POST", "/api/admin/close-room", {"roomId": rid})
    await close_cmd.finish(f"结果: {res}")

# 8. 切换模式 (循环/普通)
tmode_cmd = on_command("tmode", priority=5, permission=SUPERUSER, block=True)
@tmode_cmd.handle()
async def _(args: Message = CommandArg()):
    rid = args.extract_plain_text().strip()
    if not rid: await tmode_cmd.finish("用法: /tmode 房间ID")
    res = await req("POST", "/api/admin/toggle-mode", {"roomId": rid})
    await tmode_cmd.finish(f"结果: {res}")

# 9. 房间系统消息
smsg_cmd = on_command("smsg", priority=5, permission=SUPERUSER, block=True)
@smsg_cmd.handle()
async def _(args: Message = CommandArg()):
    txt = args.extract_plain_text().strip().split(maxsplit=1)
    if len(txt) < 2: await smsg_cmd.finish("用法: /smsg 房间ID 内容")
    res = await req("POST", "/api/admin/server-message", {"roomId": txt[0], "content": txt[1]})
    await smsg_cmd.finish(f"结果: {res}")

# 10. 批量操作
bulk_cmd = on_command("bulk", priority=5, permission=SUPERUSER, block=True)
@bulk_cmd.handle()
async def _(args: Message = CommandArg()):
    txt = args.extract_plain_text().strip().split()
    if len(txt) < 2: await bulk_cmd.finish("用法: /bulk 动作 目标 [数值]")
    payload = {"action": txt[0], "target": txt[1]}
    if len(txt) > 2: payload["value"] = txt[2]
    res = await req("POST", "/api/admin/bulk-action", payload)
    await bulk_cmd.finish(f"结果: {res}")

# 11. 封禁列表
bans_cmd = on_command("bans", priority=5, permission=SUPERUSER, block=True)
@bans_cmd.handle()
async def _():
    data = await req("GET", "/api/admin/bans")
    if isinstance(data, dict) and "error" in data:
        await bans_cmd.finish(f"查询失败: {data['error']}")
    
    msg = ["", "🚫 当前封禁列表:"]
    
    id_bans = data.get("idBans", [])
    msg.append(f"\n[用户 ID 封禁 ({len(id_bans)})]")
    if not id_bans:
        msg.append("  无")
    for b in id_bans:
        created = datetime.fromtimestamp(b['createdAt']/1000).strftime('%Y-%m-%d %H:%M')
        expires = "永久" if not b.get('expiresAt') else datetime.fromtimestamp(b['expiresAt']/1000).strftime('%Y-%m-%d %H:%M')
        msg.append(f"• ID: {b['target']} | 原因: {b['reason']}\n  管理员: {b['adminName']} | 过期: {expires}")

    ip_bans = data.get("ipBans", [])
    msg.append(f"\n[IP 封禁 ({len(ip_bans)})]")
    if not ip_bans:
        msg.append("  无")
    for b in ip_bans:
        expires = "永久" if not b.get('expiresAt') else datetime.fromtimestamp(b['expiresAt']/1000).strftime('%Y-%m-%d %H:%M')
        msg.append(f"• IP: {b['target']}\n  原因: {b['reason']}\n  过期: {expires}")

    await bans_cmd.finish("\n".join(msg))


# 12. 封禁
ban_cmd = on_command("ban", priority=5, permission=SUPERUSER, block=True)
@ban_cmd.handle()
async def _(args: Message = CommandArg()):
    txt = args.extract_plain_text().strip().split()
    if len(txt) < 2: await ban_cmd.finish("用法: /ban 类型(id/ip) 目标 [时长] [原因]")
    payload = {"type": txt[0], "target": txt[1]}
    if len(txt) > 2: payload["duration"] = txt[2]
    if len(txt) > 3: payload["reason"] = " ".join(txt[3:])
    res = await req("POST", "/api/admin/ban", payload)
    await ban_cmd.finish(f"结果: {res}")

# 13. 解封
unban_cmd = on_command("unban", priority=5, permission=SUPERUSER, block=True)
@unban_cmd.handle()
async def _(args: Message = CommandArg()):
    txt = args.extract_plain_text().strip().split()
    if len(txt) < 2: await unban_cmd.finish("用法: /unban 类型(id/ip) 目标")
    res = await req("POST", "/api/admin/unban", {"type": txt[0], "target": txt[1]})
    await unban_cmd.finish(f"结果: {res}")

# 14. 登录黑名单
blist_cmd = on_command("blist", priority=5, permission=SUPERUSER, block=True)
@blist_cmd.handle()
async def _():
    data = await req("GET", "/api/admin/login-blacklist")
    await blist_cmd.finish(f"黑名单: {data}")

# 15. 黑名单IP
blip_cmd = on_command("blip", priority=5, permission=SUPERUSER, block=True)
@blip_cmd.handle()
async def _(args: Message = CommandArg()):
    txt = args.extract_plain_text().strip().split()
    if not txt: await blip_cmd.finish("用法: /blip IP [时长]")
    payload = {"ip": txt[0]}
    if len(txt) > 1: payload["duration"] = txt[1]
    res = await req("POST", "/api/admin/blacklist-ip", payload)
    await blip_cmd.finish(f"结果: {res}")

# 16. 移除黑名单IP
ublip_cmd = on_command("ublip", priority=5, permission=SUPERUSER, block=True)
@ublip_cmd.handle()
async def _(args: Message = CommandArg()):
    ip = args.extract_plain_text().strip()
    if not ip: await ublip_cmd.finish("用法: /ublip IP")
    res = await req("POST", "/api/admin/unblacklist-ip", {"ip": ip})
    await ublip_cmd.finish(f"结果: {res}")

