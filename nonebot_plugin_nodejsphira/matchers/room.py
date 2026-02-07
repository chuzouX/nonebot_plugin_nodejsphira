from nonebot import on_command
from nonebot.adapters.qq import Bot, Event, MessageSegment
from nonebot.params import CommandArg
from nonebot.adapters.qq.message import Message
from nonebot.log import logger
from nonebot.plugin import get_plugin_config
import asyncio

from ..config import Config
from ..utils.api import fetch_json
from ..utils.render import capture_url

plugin_config = get_plugin_config(Config)

# 指令 1: /room (文字版)
room_text_cmd = on_command("room", priority=5, block=True)

@room_text_cmd.handle()
async def handle_room_text(bot: Bot, event: Event, args: Message = CommandArg()):
    room_id = args.extract_plain_text().strip().strip('"').strip("'")
    api_url = f"{plugin_config.phira_api_url}/api/status"
    
    try:
        data = await fetch_json(api_url)
    except Exception as e:
        await room_text_cmd.finish(f"查询失败: {e}")
        return

    server_name = data.get("serverName", "Unknown")
    rooms = data.get("rooms", [])

    if room_id:
        target = next((r for r in rooms if str(r.get("id")) == room_id), None)
        if not target:
            await room_text_cmd.finish(f"\n❌ 未找到房间 {room_id}")
            return
            
        rid = target.get("id")
        name = target.get("name")
        pc = target.get("playerCount")
        mp = target.get("maxPlayers")
        locked = "已锁定 🔒" if target.get("locked") else "开放中 🔓"
        chart = target.get("state", {}).get("chartName") or "等待选曲"
        players = target.get("players", [])
        
        # 详情模式的房主识别
        owner_id = target.get("ownerId")
        owner_name = "未知"
        if players:
            if owner_id:
                owner_obj = next((p for p in players if p.get("id") == owner_id), players[0])
                owner_name = owner_obj.get("name", "Unknown")
            else:
                owner_name = players[0].get("name", "Unknown")

        p_list = "\n".join([f"  • {p['name']} (ID: {p['id']})" for p in players]) if players else "  (暂无玩家)"
        
        msg = (
            f"\n🏠 服务器: {server_name}\n"
            f"━━━━━━━━━━━━━━\n"
            f"🔍 房间详情 (ID: {rid})\n"
            f"🚪 名称: {name}\n"
            f"👑 房主: {owner_name}\n"
            f"🔐 状态: {locked}\n"
            f"📊 人数: {pc}/{mp}\n"
            f"⚙️ 状态: {target.get('state', {}).get('type', 'Unknown')}\n"
            f"🎵 歌曲: {chart}\n"
            f"👥 玩家列表:\n{p_list}"
        )
        await room_text_cmd.finish(msg)
    else:
        # 列表概览模式
        header = [
            "", # 第一行留空
            f"🏠 服务器: {server_name}",
            f"👥 在线人数: {data.get('onlinePlayers', 0)} | 🚪 房间总数: {data.get('roomCount', 0)}",
            "━━━━━━━━━━━━━━"
        ]
        
        if not rooms:
            header.append("💡 当前暂无活跃房间。")
            await room_text_cmd.finish("\n".join(header))
        else:
            room_list_msgs = []
            for r in rooms:
                rid = r.get("id")
                name = r.get("name")
                pc = r.get("playerCount")
                mp = r.get("maxPlayers")
                locked_icon = "🔒" if r.get("locked") else "🔓"
                chart = r.get("state", {}).get("chartName") or "等待选曲"
                
                # 房主识别
                players_list = r.get("players", [])
                owner_id = r.get("ownerId")
                owner_name = "未知"
                if players_list:
                    if owner_id:
                        owner_obj = next((p for p in players_list if p.get("id") == owner_id), players_list[0])
                        owner_name = owner_obj.get("name", "Unknown")
                    else:
                        owner_name = players_list[0].get("name", "Unknown")
                
                players_names = "、".join([p["name"] for p in players_list])
                
                room_block = (
                    f"{locked_icon} 房间: {name} (ID: {rid})\n"
                    f"📊 人数: {pc}/{mp} | 🎵: {chart}\n"
                    f"👑 房主: {owner_name}\n"
                    f"👤 玩家: {players_names if players_names else '(暂无)'}"
                )
                room_list_msgs.append(room_block)
            
            final_msg = "\n".join(header) + "\n" + "\n\n".join(room_list_msgs)
            await room_text_cmd.finish(final_msg)


# 指令 2: /proom (截图版)
proom_cmd = on_command("proom", priority=5, block=True)

@proom_cmd.handle()
async def handle_proom(bot: Bot, event: Event, args: Message = CommandArg()):
    room_id = args.extract_plain_text().strip().strip('"').strip("'")
    
    if room_id:
        url = f"{plugin_config.phira_api_url}/room.html?id={room_id}"
        width = plugin_config.phira_screenshot_width_pc
        is_mobile = False
    else:
        url = plugin_config.phira_api_url
        width = plugin_config.phira_screenshot_width_mobile
        is_mobile = True

    receipt = await proom_cmd.send("正在查询中.....")
    msg_id = None
    if receipt:
        if isinstance(receipt, dict): msg_id = receipt.get("id")
        else: msg_id = getattr(receipt, "id", None)

    try:
        pic = await capture_url(
            url=url,
            width=width,
            height=1080, # 基础高度
            wait_time=plugin_config.phira_screenshot_wait_time,
            is_mobile=is_mobile
        )
        await proom_cmd.send(MessageSegment.file_image(pic))
    except Exception as e:
        logger.error(f"截图失败: {e}")
        await proom_cmd.send(f"截图失败: {e}")
    finally:
        if msg_id:
            try:
                await asyncio.sleep(1)
                group_openid = getattr(event, "group_openid", None)
                channel_id = getattr(event, "channel_id", None)
                author = getattr(event, "author", None)
                user_openid = getattr(author, "user_openid", None) if author else None

                if group_openid:
                    await bot.delete_group_message(group_openid=group_openid, message_id=msg_id)
                elif channel_id:
                    await bot.delete_message(channel_id=channel_id, message_id=msg_id)
                elif user_openid:
                    await bot.delete_c2c_message(openid=user_openid, message_id=msg_id)
            except Exception:
                pass