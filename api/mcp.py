#!/usr/bin/env python3
"""
Vercel Serverless Function for HK Transport MCP
"""
import sys
import os

# 添加項目根目錄到 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'src'))

# 導入並初始化 MCP
try:
    from src.server import mcp
    # 創建 ASGI 應用程式使用 SSE transport
    app = mcp.http_app(transport="sse", stateless_http=True)
except Exception as e:
    print(f"Error loading MCP: {e}", file=sys.stderr)
    raise

# 使用 Mangum 將 ASGI 轉換為 AWS Lambda/Vercel handler
try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
except ImportError as e:
    print(f"Error: Mangum not installed: {e}", file=sys.stderr)
    print("Please add 'mangum' to requirements.txt", file=sys.stderr)
    raise
