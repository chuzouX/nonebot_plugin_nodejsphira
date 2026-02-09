from nonebot import on_command
from nonebot.adapters.qq import Bot, Event, MessageSegment
from nonebot.plugin import get_plugin_config
from nonebot.log import logger
import asyncio

from ..config import Config
from ..utils.render import capture_url
from ..utils.phira_check import get_phira_token, test_phira_tcp

plugin_config = get_plugin_config(Config)

# --- 新的 /status 指令 (TCP 检测) ---
status_check_cmd = on_command("status", priority=5, block=True)

@status_check_cmd.handle()
async def handle_status_check(bot: Bot, event: Event):
    if not plugin_config.phira_check_email or not plugin_config.phira_check_password:
        await status_check_cmd.finish("❌ 未配置检测账号，请在 .env 中设置 PHIRA_CHECK_EMAIL 和 PHIRA_CHECK_PASSWORD")

    # 解析服务器地址
    server = plugin_config.phira_check_server
    if ":" in server:
        host, port_str = server.rsplit(":", 1)
        port = int(port_str)
    else:
        host, port = server, 12346

    # QQ 适配器对 URL 极其敏感，将域名中的点替换掉以绕过检测
    safe_host = host.replace(".", "[.]")

    receipt = await status_check_cmd.send(f"🔍 正在对 {safe_host}:{port} 进行协议握手检测...")

    try:
        # 1. 获取 Token
        token = await get_phira_token(plugin_config.phira_check_email, plugin_config.phira_check_password)
        
        # 2. 测试 TCP
        success, message, latency = await test_phira_tcp(host, port, token)
        
        # 3. 输出结果
        status_icon = "✅" if success else "❌"
        result = [
            "",
            f"{status_icon} Phira 协议检测结果",
            "━━━━━━━━━━━━━━",
            f"目标: {plugin_config.phira_server_name}",
            f"状态: {'在线' if success else '异常'}",
            f"详情: {message}"
        ]
        if success:
            result.append(f"延迟: {latency:.2f}ms")
        
        await status_check_cmd.send("\n".join(result))

    except Exception as e:
        logger.error(f"检测过程出错: {e}")
        await status_check_cmd.send(f"❌ 检测失败: {e}")
    
    finally:
        # 撤回提示消息
        msg_id = getattr(receipt, "id", None) if receipt else None
        if isinstance(receipt, dict): msg_id = receipt.get("id")
        if msg_id:
            await asyncio.sleep(1)
            try:
                group_id = getattr(event, "group_openid", None)
                channel_id = getattr(event, "channel_id", None)
                if group_id: await bot.delete_group_message(group_openid=group_id, message_id=msg_id)
                elif channel_id: await bot.delete_message(channel_id=channel_id, message_id=msg_id)
            except: pass

# --- 旧的 /status 挪到 /pstatus (网页截图) ---
pstatus_cmd = on_command("pstatus", priority=5, block=True)

@pstatus_cmd.handle()
async def handle_pstatus(bot: Bot, event: Event):
    url = plugin_config.phira_status_page_url
    receipt = await pstatus_cmd.send("正在获取 Phira 服务器状态图.....")

    try:
        pic = await capture_url(url=url, width=1280, height=720, wait_time=3000)
        await pstatus_cmd.send(MessageSegment.file_image(pic))
    except Exception as e:
        await pstatus_cmd.send(f"获取截图失败: {e}")
    
    finally:
        msg_id = getattr(receipt, "id", None) if receipt else None
        if isinstance(receipt, dict): msg_id = receipt.get("id")
        if msg_id:
            await asyncio.sleep(1)
            try:
                group_id = getattr(event, "group_openid", None)
                channel_id = getattr(event, "channel_id", None)
                if group_id: await bot.delete_group_message(group_openid=group_id, message_id=msg_id)
                elif channel_id: await bot.delete_message(channel_id=channel_id, message_id=msg_id)
            except: pass
