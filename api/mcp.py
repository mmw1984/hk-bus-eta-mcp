#!/usr/bin/env python3
"""
Vercel Serverless Function for HK Transport MCP

Vercel 原生支援 ASGI 應用程式，只需要定義 `app` 變數即可。
FastMCP 的 http_app() 返回 Starlette ASGI 應用。
"""
import sys
import os

# 添加項目根目錄到 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'src'))

# 導入並初始化 MCP
from src.server import mcp

# 創建 ASGI 應用程式 - Vercel 原生支援 ASGI
# 使用 streamable-http transport（推薦用於 serverless）
app = mcp.http_app()
