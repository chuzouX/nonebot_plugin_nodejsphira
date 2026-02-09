import asyncio
import httpx
import time
from typing import Dict, Any, Tuple

def encode_varint(value: int) -> bytes:
    """Varint 编码实现"""
    result = bytearray()
    while True:
        b = value & 0x7f
        value >>= 7
        if value != 0:
            b |= 0x80
        result.append(b)
        if value == 0:
            break
    return bytes(result)

async def get_phira_token(email: str, password: str) -> str:
    """获取 Phira 登录 Token"""
    url = "https://phira.5wyxi.com/login"
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url, 
            json={"email": email, "password": password},
            headers={"User-Agent": "PhiraChecker/2.1"},
            timeout=10.0
        )
        if resp.status_code != 200:
            raise RuntimeError(f"登录失败 ({resp.status_code})")
        data = resp.json()
        token = data.get("token")
        if not token:
            raise RuntimeError("未返回有效 Token")
        return token

async def test_phira_tcp(host: str, port: int, token: str) -> Tuple[bool, str, float]:
    """执行 TCP 握手检测"""
    start_time = time.perf_counter()
    try:
        # 1. 建立连接
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), 
            timeout=5.0
        )
        
        try:
            # 2. 发送初始握手标识
            writer.write(b'\x01')
            await writer.drain()
            
            # 3. 构建内部数据包 [0x01, varint(token_len), token_bytes]
            token_bytes = token.encode('utf-8')
            inner_packet = b'\x01' + encode_varint(len(token_bytes)) + token_bytes
            
            # 4. 发送 [varint(packet_len), inner_packet]
            writer.write(encode_varint(len(inner_packet)))
            writer.write(inner_packet)
            await writer.drain()
            
            # 5. 读取响应
            data = await asyncio.wait_for(reader.read(1024), timeout=5.0)
            
            latency = (time.perf_counter() - start_time) * 1000
            if data:
                return True, "握手成功", latency
            else:
                return False, "服务端主动断开连接", latency
                
        finally:
            writer.close()
            await writer.wait_closed()
            
    except asyncio.TimeoutError:
        return False, "连接或响应超时", 0.0
    except Exception as e:
        return False, f"网络异常: {str(e)}", 0.0
