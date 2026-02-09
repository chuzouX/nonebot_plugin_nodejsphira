from typing import Optional
from pydantic import BaseModel

class Config(BaseModel):
    # Phira WEB服务器基础地址
    phira_api_url: str = "https://phira.chuzoux.top"
    
    # Phira 状态页截图地址
    phira_status_page_url: str = "https://status.dmocken.top/status/phira"
    
    # Phira 管理员密钥
    phira_admin_secret: Optional[str] = None
    
    # --- 新增：Phira TCP 检测配置 ---
    # 用于检测的 Phira 账号邮箱
    phira_check_email: Optional[str] = None
    # 用于检测的 Phira 账号密码
    phira_check_password: Optional[str] = None
    # 默认检测的服务器地址 (host:port)
    phira_check_server: str = "mp.phira.cn:12346"
    # 用于展示的 Phira 服务器名称
    phira_server_name: Optional[str] = None
    
    # 截图相关配置
    phira_screenshot_width_pc: int = 1536
    phira_screenshot_width_mobile: int = 414
    phira_screenshot_timeout: int = 60000
    phira_screenshot_wait_time: int = 2000
    
    class Config:
        extra = "ignore"