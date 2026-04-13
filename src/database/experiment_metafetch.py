# experiment_metafetch.py
import sys
import os
import time
from datetime import datetime
import requests

# 确保能找到 src 下的模块
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from database.db_manager import DBManager
from core.states import MainState

DB_PATH = "aliya.db"

# 天气 API 配置 (北京)
LATITUDE = 39.9042
LONGITUDE = 116.4074
WEATHER_API_URL = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current_weather=true"

def get_current_time_iso() -> str:
    """获取当前时间的 ISO 格式字符串"""
    return datetime.now().isoformat()

def fetch_weather() -> str:
    """调用 Open-Meteo API 获取天气概况"""
    try:
        response = requests.get(WEATHER_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        current = data.get("current_weather", {})
        temp = current.get("temperature")
        windspeed = current.get("windspeed")
        weather_code = current.get("weathercode")
        
        # 简单拼凑成易读的自然语言，符合 [0] Meta 的拟人化需求
        return f"气温 {temp}℃, 风速 {windspeed}km/h, 天气代码 {weather_code}"
    except Exception as e:
        return f"无法获取天气: {str(e)}"

def update_meta_cache(db: DBManager, key: str, value: str) -> None:
    """向 meta_cache 表中插入或替换指定 key 的值"""
    query = "INSERT OR REPLACE INTO meta_cache (key, value, updated_at) VALUES (?, ?, ?)"
    # 这里手动传入 datetime.now() 确保 updated_at 同步更新（若 schema 没写触发器）
    db.execute_and_commit(query, (key, value, datetime.now()))

def run_meta_loop(interval_seconds: int = 60):
    """
    元数据刷新主循环
    - interval_seconds: 刷新的间隔（即你要求的断点/速率限制）
    """
    db = DBManager(DB_PATH)
    db.connect()
    
    # 模拟外部状态读取（实际项目中应从共享内存或数据库读取当前系统状态）
    # 这里演示逻辑：如果检测到系统处于 BUSY_COGNITION，则跳过刷新以保护 I/O
    print(f"[MetaFetcher] 启动，刷新频率: {interval_seconds}s")
    
    try:
        while True:
            # 模拟：获取当前系统状态（此处暂用模拟变量，真实场景应查 DB 或 共享状态）
            current_system_state = MainState.IDLE # 这是一个占位模拟
            
            if not current_system_state.allows_background_io:
                print(f"[MetaFetcher] 当前系统状态为 {current_system_state.name}，按停 IO 服务...")
            else:
                # 1. 更新时间
                time_str = get_current_time_iso()
                update_meta_cache(db, "time", time_str)
                
                # 2. 更新天气
                weather_str = fetch_weather()
                update_meta_cache(db, "weather", weather_str)
                
                print(f"[{time.strftime('%H:%M:%S')}] ✓ 元数据已刷新 (Time & Weather)")

            # 3. 速率限制断点
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("[MetaFetcher] 已停止。")
    finally:
        db.close()

if __name__ == "__main__":
    # 默认 10 秒刷新一次，方便测试
    run_meta_loop(interval_seconds=10)