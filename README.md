<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-nodejsphira

✨ **Phira 游戏服务器管理与监控插件** ✨

适用于 NoneBot2 的 Phira Multiplayer (Node.js 版) 后端管理插件。提供实时的房间查询、网页截图监控、服务器协议级连通性检测以及完整的管理员远程控制功能。

## 📖 功能介绍

- **多维度房间查询**：支持纯文本列表展示及高清网页长截图（PC/移动端布局）。
- **连通性检测**：模拟 Phira 客户端进行 TCP 协议级握手测试，获取真实延迟。
- **状态监控**：一键获取 Phira 服务器各节点的运行状态截图。
- **动态鉴权管理**：集成 AES-256-CBC 动态加密算法，安全对接管理接口。
- **全方位行政指令**：支持广播、踢人、强制开始、切换锁定、修改人数上限、关闭房间等。

## 💿 安装方法

推荐使用 `nb-cli` 进行安装：

```bash
nb plugin install nonebot-plugin-nodejsphira
```

并在机器人 `.env` 文件中配置必要项。

> **注意**：网页截图功能依赖 `nonebot-plugin-htmlrender`。安装后请务必执行：
> ```bash
> playwright install chromium
> ```

## ⚙️ 插件配置项

在机器人的 `.env` 文件中添加以下配置：

| 配置项 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `PHIRA_API_URL` | str | `https://phira.chuzoux.top` | Phira WEB服务器基础地址 |
| `PHIRA_STATUS_PAGE_URL` | str | `https://status.dmocken.top/status/phira` | Phira 状态页截图地址 |
| `PHIRA_CHECK_EMAIL` | str | 无 | Phira 检测账号邮箱 (用于 /status) |
| `PHIRA_CHECK_PASSWORD` | str | 无 | Phira 检测账号密码 (用于 /status) |
| `PHIRA_CHECK_SERVER` | str | `mp.phira.cn:12346` | 默认检测的 TCP 服务器地址 |
| `PHIRA_SERVER_NAME` | str | 无 | Phira 服务器名称展示 (用于 /status) |
| `PHIRA_ADMIN_SECRET` | str | 无 | **必填**。需在 [phira-mp-nodejsver](https://github.com/chuzouX/phira-mp-nodejsver) 项目中设置 |
| `SUPERUSERS` | list | `[]` | 机器人管理员列表 (OpenID) |

## 🎮 触发规则

### 基础指令 (所有用户)
- `/room` : 获取服务器房间概览列表 (纯文本)。
- `/proom` : 以移动端尺寸获取房间列表的网页长截图。
- `/status` : 执行 Phira 服务器协议级握手检测 (TCP，返回延迟)。
- `/pstatus` : 获取 Phira 服务器节点运行状态图 (截图)。
- `/ping` : 查看机器人在线状态及当前用户权限。
- `/help` : 显示帮助菜单。

### 管理指令 (仅 SUPERUSERS)
- `/players` : 列出全服所有活跃玩家。
- `/broadcast "内容" [#ID]` : 全服或指定房间广播系统消息。
- `/kick {UID}` : 强制踢出指定 ID 的玩家。
- `/fstart {RID}`, `/lock {RID}`, `/maxp {RID} {人数}`, `/close {RID}` : 房间行政管理。

## 🛠️ 其它用法

### 协议检测原理
`/status` 指令会模拟登录 `phira.5wyxi.com` 获取 Token，随后与目标服务器建立 TCP 连接并发送 `0x01` 握手包。如果收到正确响应，则判定为“在线”并计算往返延迟。

## 📝 许可证
MIT