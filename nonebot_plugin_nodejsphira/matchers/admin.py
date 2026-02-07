from nonebot import on_command, get_driver
from nonebot.adapters.qq import Message, Bot, Event
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import get_plugin_config

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
