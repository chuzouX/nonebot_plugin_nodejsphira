from nonebot import on_command, get_driver
from nonebot.adapters.qq import Bot, Event

config = get_driver().config
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
        "/proom - 查看房间列表长截图 (网页截图)\n",
        "/status - Phira 服务器协议握手检测 (文本)\n",
        "/pstatus - 查看 Phira 节点运行状态图 (网页截图)\n",
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
            "/close {RID} - 强制关闭指定房间\n",
            "/tmode {RID} - 切换房间模式 (循环/普通)\n",
            "/smsg {RID} {内容} - 发送房间系统消息\n",
            "/bulk {动作} {目标} [值] - 批量房间操作\n",
            "/bans - 查看封禁列表\n",
            "/ban {类型} {目标} [时长] [原因] - 执行封禁\n",
            "/unban {类型} {目标} - 解除封禁\n",
            "/blist - 查看登录黑名单\n",
            "/blip {IP} [时长] - 黑名单 IP\n",
            "/ublip {IP} - 移除黑名单 IP\n"
        ])
    else:
        help_msg.append("提示: 管理员功能仅限配置文件中设置的 SUPERUSERS 使用")

    await help_cmd.finish("".join(help_msg))
