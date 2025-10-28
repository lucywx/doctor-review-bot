#!/usr/bin/env python3
"""
直接检查Railway环境变量的实际值
通过创建一个调试端点来检查环境变量
"""

import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

@app.get("/debug-env")
async def debug_env():
    """调试环境变量"""
    
    # 直接读取环境变量
    raw_env_vars = {
        "GOOGLE_PLACES_API_KEY": os.getenv("GOOGLE_PLACES_API_KEY"),
        "GOOGLE_SEARCH_API_KEY": os.getenv("GOOGLE_SEARCH_API_KEY"),
        "GOOGLE_SEARCH_ENGINE_ID": os.getenv("GOOGLE_SEARCH_ENGINE_ID"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    }
    
    # 检查每个变量的详细信息
    env_details = {}
    for key, value in raw_env_vars.items():
        if value is None:
            env_details[key] = {
                "value": None,
                "type": "None",
                "length": 0,
                "is_empty": True,
                "is_not_required": False
            }
        else:
            env_details[key] = {
                "value": value,
                "type": type(value).__name__,
                "length": len(value),
                "is_empty": len(value) == 0,
                "is_not_required": value == "not_required",
                "starts_with": value[:10] if len(value) >= 10 else value,
                "ends_with": value[-10:] if len(value) >= 10 else value
            }
    
    # 检查Google Places API特定逻辑
    google_places_key = os.getenv("GOOGLE_PLACES_API_KEY")
    places_api_configured = (
        google_places_key is not None and 
        google_places_key != "not_required" and
        len(google_places_key) > 10
    )
    
    return JSONResponse({
        "environment_variables": env_details,
        "google_places_configured": places_api_configured,
        "google_places_key_value": google_places_key,
        "all_env_vars": dict(os.environ)
    })

@app.get("/health")
async def health():
    return {"status": "healthy", "environment": "production", "database": "connected"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
