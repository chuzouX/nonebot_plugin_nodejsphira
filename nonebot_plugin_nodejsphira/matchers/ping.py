from nonebot import on_command, get_driver
from nonebot.adapters.qq import Bot, Event
from nonebot.log import logger

try:
    from nonebot_plugin_status import render_template
except ImportError:
    render_template = None

config = get_driver().config
# 恢复为从 NoneBot 配置动态读取，移除硬编码 ID
superusers = getattr(config, "superusers", set())

ping_cmd = on_command("ping", priority=1, block=True)

@ping_cmd.handle()
async def handle_ping(bot: Bot, event: Event):
    user_id = event.get_user_id()
    is_admin = user_id in superusers
    
    perm_text = "管理员" if is_admin else "普通用户"
    msg = f"Pong! 机器人在线中。\n您的权限: {perm_text}"
    
    if render_template:
        try:
            status = await render_template()
            msg += f"\n\n{status}"
        except Exception as e:
            logger.error(f"获取状态失败: {e}")
            
    await ping_cmd.finish(msg)