from nonebot import require
from nonebot.log import logger

try:
    require("nonebot_plugin_htmlrender")
    from nonebot_plugin_htmlrender import get_new_page
except Exception:
    logger.error("请安装 nonebot-plugin-htmlrender 以使用截图功能")
    get_new_page = None

async def capture_url(
    url: str,
    width: int = 1536,
    height: int = 1080,
    wait_time: int = 2000,
    device_scale_factor: float = 2.0,
    is_mobile: bool = False,
    timeout: int = 60000
) -> bytes:
    """通用的网页截图工具函数"""
    if not get_new_page:
        raise RuntimeError("依赖 nonebot_plugin_htmlrender 未加载")

    async with get_new_page(
        viewport={"width": width, "height": height},
        device_scale_factor=device_scale_factor
    ) as page:
        try:
            if is_mobile:
                await page.set_extra_http_headers({
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1"
                })
            
            await page.goto(url, wait_until="networkidle", timeout=timeout)
        except Exception as e:
            logger.warning(f"网页加载等待超时 (networkidle): {e}")
        
        # 注入通用 CSS 修复
        await page.add_style_tag(content="body { zoom: 1.25 !important; }")
        await page.add_style_tag(content="""
            html, body, #root, #app, .v-application, .v-application--wrap {
                height: auto !important;
                min-height: auto !important;
                overflow: visible !important;
                position: static !important;
            }
        """)
        
        # 等待数据渲染
        await page.wait_for_timeout(wait_time)
        
        # 强制滚动触发
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(500)
        await page.evaluate("window.scrollTo(0, 0)")
        
        return await page.screenshot(full_page=True)