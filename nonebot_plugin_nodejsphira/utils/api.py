import hashlib
import os
import httpx
from datetime import datetime
from typing import Optional, Dict, Any
from nonebot.log import logger

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.backends import default_backend
except ImportError:
    logger.error("缺少 cryptography 库，Phira 管理功能将无法正常工作")

def generate_dynamic_secret(admin_secret: str) -> str:
    """生成当日有效的加密鉴权串"""
    if not admin_secret:
        raise ValueError("Admin secret is empty")

    date_str = datetime.now().strftime("%Y-%m-%d")
    plain_text = f"{date_str}_{admin_secret}_xy521"
    
    key = hashlib.sha256(admin_secret.encode('utf-8')).digest()
    iv = os.urandom(16)
    
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plain_text.encode('utf-8')) + padder.finalize()
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    return (iv + ciphertext).hex()

async def fetch_json(url: str, params: Optional[Dict] = None, timeout: float = 10.0) -> Any:
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=timeout)
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code}")
        return resp.json()

async def admin_request(
    base_url: str, 
    secret: str, 
    method: str, 
    endpoint: str, 
    json_data: Optional[dict] = None
) -> Dict:
    """执行管理请求"""
    try:
        token = generate_dynamic_secret(secret)
    except Exception as e:
        return {"error": f"鉴权生成失败: {e}"}
        
    headers = {"X-Admin-Secret": token}
    url = f"{base_url.rstrip('/')}{endpoint}"
    
    async with httpx.AsyncClient() as client:
        try:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, timeout=15.0)
            else:
                response = await client.post(url, headers=headers, json=json_data, timeout=15.0)
            return response.json()
        except Exception as e:
            logger.error(f"API 请求失败: {e}")
            return {"error": str(e)}