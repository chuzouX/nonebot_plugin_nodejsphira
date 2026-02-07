from nonebot import on_command, get_driver
from nonebot.adapters.qq import Bot, Event

config = get_driver().config
# 恢复为从 NoneBot 配置动态读取，移除硬编码 ID
superusers = getattr(config, "superusers", set())

help_cmd = on_command("help", aliases={"帮助"}, priority=5, block=True)

@help_cmd.handle()
async def _(bot: Bot, event: Event):
    user_id = event.get_user_id()
    is_admin = user_id in superusers

    help_msg = [
        "\n",
        "--- FunXLink_Bot 帮助菜单 ---\n",
        "📖 基础命令:\n",
        "/room - 获取服务器房间列表 (文本详情)\n",
        "/room {id} - 获取指定房间详细列表 (文本详情)\n",
        "/proom - 查看房间列表长截图 (网页截图)\n",
        "/proom {id} - 查看指定房间详细画面 (网页截图)\n",
        "/status - 查看 Phira 服务器运行状态\n",
        "/ping - 查看机器人及服务器连接延迟\n",
        "/help - 显示本帮助菜单\n"
    ]

    if is_admin:
        help_msg.extend([
            "\n",
            "⚙️ 管理员命令:\n",
            "/players - 查看当前所有在线玩家列表\n",
            "/broadcast \"内容\" [#ID] - 全服或指定房间广播\n",
            "/kick {UID} - 强制移除指定用户\n",
            "/fstart {RID} - 强制开始指定房间对局\n",
            "/lock {RID} - 锁定/解锁房间\n",
            "/maxp {RID} {人数} - 修改房间最大人数限制\n",
            "/close {RID} - 强制关闭指定房间\n"
        ])
    else:
        help_msg.append("提示: 管理员功能仅限配置文件中设置的 SUPERUSERS 使用")

    await help_cmd.finish("".join(help_msg))