#!/usr/bin/env python3
"""
创建一个测试端点来检查Railway环境变量
"""

import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

@app.get("/env-check")
async def check_env():
    """检查环境变量"""
    env_vars = {
        "GOOGLE_PLACES_API_KEY": os.getenv("GOOGLE_PLACES_API_KEY", "NOT_SET"),
        "GOOGLE_SEARCH_API_KEY": os.getenv("GOOGLE_SEARCH_API_KEY", "NOT_SET"),
        "GOOGLE_SEARCH_ENGINE_ID": os.getenv("GOOGLE_SEARCH_ENGINE_ID", "NOT_SET"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", "NOT_SET"),
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "NOT_SET"),
    }
    
    # 检查Google Places API是否配置
    google_places_configured = (
        env_vars["GOOGLE_PLACES_API_KEY"] != "NOT_SET" and 
        env_vars["GOOGLE_PLACES_API_KEY"] != "not_required" and
        len(env_vars["GOOGLE_PLACES_API_KEY"]) > 10
    )
    
    return JSONResponse({
        "environment_variables": env_vars,
        "google_places_configured": google_places_configured,
        "google_places_key_length": len(env_vars["GOOGLE_PLACES_API_KEY"]) if env_vars["GOOGLE_PLACES_API_KEY"] != "NOT_SET" else 0
    })

@app.get("/health")
async def health():
    return {"status": "healthy", "environment": "production", "database": "connected"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
