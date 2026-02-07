# nonebot-plugin-nodejsphira

✨ **Phira 游戏服务器管理与监控插件** ✨

适用于 NoneBot2 的 Phira Multiplayer (Node.js 版) 后端管理插件。提供实时的房间查询、网页截图监控、服务器节点状态查看以及完整的管理员远程控制功能。

## 📖 功能介绍

- **多维度房间查询**：支持纯文本列表展示及高清网页长截图（PC/移动端布局）。
- **实时状态监控**：一键获取 Phira 服务器各节点的运行状态。
- **动态鉴权管理**：集成 AES-256-CBC 动态加密算法，安全对接管理接口。
- **全方位行政指令**：支持广播、踢人、强制开始、切换锁定、修改人数上限、关闭房间等。
- **权限智能感知**：帮助菜单根据用户权限（SUPERUSERS）动态显示指令。

## 💿 安装方法

推荐使用 `nb-cli` 进行安装：

```bash
nb plugin install nonebot-plugin-nodejsphira
```

或者使用 `pip` 安装后手动加载：

```bash
pip install nonebot-plugin-nodejsphira
```

并在 `pyproject.toml` 或 `bot.py` 中加载插件：
```toml
plugins = ["nonebot_plugin_nodejsphira"]
```

> **注意**：本插件依赖 `nonebot-plugin-htmlrender` 进行网页截图。安装后请务必执行以下命令安装浏览器内核：
> ```bash
> playwright install chromium
> ```

## ⚙️ 插件配置项

在机器人的 `.env` 文件中添加以下配置：

| 配置项 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `PHIRA_API_URL` | str | `https://phira.chuzoux.top` | Phira WEB服务器基础地址 |
| `PHIRA_STATUS_PAGE_URL` | str | `https://status.dmocken.top/status/phira` | Phira 状态页截图地址 |
| `PHIRA_ADMIN_SECRET` | str | 无 | **必填**。需在 [phira-mp-nodejsver](https://github.com/chuzouX/phira-mp-nodejsver) 项目中设置，用于鉴权 |
| `PHIRA_SCREENSHOT_WAIT_TIME` | int | `2000` | 截图等待时间 (ms) |
| `PHIRA_SCREENSHOT_TIMEOUT` | int | `60000` | 截图超时时间 (ms) |
| `SUPERUSERS` | list | `[]` | 机器人管理员列表 (OpenID)，拥有管理指令权限 |

## 🎮 触发规则

### 基础指令 (所有用户)
- `/room` : 获取服务器房间概览列表 (纯文本，包含房主及玩家)。
- `/room {id}` : 查询指定房间的详细玩家名单及状态 (纯文本)。
- `/proom` : 以移动端尺寸获取房间列表的网页长截图。
- `/proom {id}` : 获取指定房间详情的网页截图 (PC布局)。
- `/status` : 获取 Phira 服务器运行状态图。
- `/ping` : 查看机器人在线状态及当前用户权限。
- `/help` : 显示帮助菜单。

### 管理指令 (仅 SUPERUSERS)
- `/players` : 列出全服所有房间内的在线玩家。
- `/broadcast "内容" [#ID]` : 向全服或指定房间发送系统广播。
- `/kick {UID}` : 强制将指定 ID 的玩家移出服务器。
- `/fstart {RID}` : 强制开始指定房间的游戏。
- `/lock {RID}` : 切换房间的锁定/解锁状态。
- `/maxp {RID} {人数}` : 修改指定房间的人数上限。
- `/close {RID}` : 强制解散并关闭指定房间。

## 🛠️ 其它用法

### 视觉缩放说明
插件默认开启了 **125% 的视觉缩放** 以及 **2.0 的像素密度**，确保生成的截图在手机端查看时，文字清晰且布局紧凑。

### 动态鉴权
管理指令会自动读取 `PHIRA_ADMIN_SECRET` 并生成当日有效的加密串。请确保机器人服务器的系统时间准确，否则会导致鉴权失败。

## 📝 许可证
MIT
