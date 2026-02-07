from typing import Optional
from pydantic import BaseModel

class Config(BaseModel):
    # Phira WEB服务器基础地址
    phira_api_url: str = "https://phira.chuzoux.top"
    
    # Phira 状态页截图地址
    phira_status_page_url: str = "https://status.dmocken.top/status/phira"
    
    # Phira 管理员密钥 (可通过环境变量 PHIRA_ADMIN_SECRET 配置)
    # 需在对应项目 https://github.com/chuzouX/phira-mp-nodejsver 中设置，用于管理鉴权
    phira_admin_secret: Optional[str] = None
    
    # 截图相关配置
    phira_screenshot_width_pc: int = 1536
    phira_screenshot_width_mobile: int = 414
    phira_screenshot_timeout: int = 60000
    phira_screenshot_wait_time: int = 2000
    
    class Config:
        extra = "ignore"
