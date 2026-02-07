from nonebot import require
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_htmlrender")

from .config import Config
from .matchers import room, status, ping, admin, help

__plugin_meta__ = PluginMetadata(
    name="Phira Server Manager",
    description="Phira 游戏服务器管理与监控插件",
    usage="/help 查看指令列表",
    type="application",
    homepage="https://github.com/chuzouX/nonebot_plugin_nodejsphira",
    config=Config,
    supported_adapters={"~qq"},
)
