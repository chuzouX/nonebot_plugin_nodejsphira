from nonebot import on_command
from nonebot.adapters.qq import Bot, Event, MessageSegment
from nonebot.plugin import get_plugin_config
from nonebot.log import logger
import asyncio

from ..config import Config
from ..utils.render import capture_url

plugin_config = get_plugin_config(Config)

status_cmd = on_command("status", priority=5, block=True)

@status_cmd.handle()
async def handle_status(bot: Bot, event: Event):
    url = plugin_config.phira_status_page_url
    
    receipt = await status_cmd.send("正在获取 Phira 服务器状态.....")
    msg_id = getattr(receipt, "id", None) if receipt else None
    if isinstance(receipt, dict): msg_id = receipt.get("id")

    try:
        pic = await capture_url(
            url=url,
            width=1280,
            height=720,
            wait_time=3000
        )
        await status_cmd.send(MessageSegment.file_image(pic))
    except Exception as e:
        logger.error(f"状态页截图失败: {e}")
        await status_cmd.send(f"获取状态失败: {e}")
    finally:
        if msg_id:
            try:
                await asyncio.sleep(1)
                if hasattr(bot, "delete_group_message") and getattr(event, "group_openid", None):
                    await bot.delete_group_message(group_openid=event.group_openid, message_id=msg_id)
                elif hasattr(bot, "delete_message") and getattr(event, "channel_id", None):
                    await bot.delete_message(channel_id=event.channel_id, message_id=msg_id)
                elif hasattr(bot, "delete_c2c_message") and getattr(event, "author", None):
                    await bot.delete_c2c_message(openid=event.author.user_openid, message_id=msg_id)
            except Exception:
                pass
