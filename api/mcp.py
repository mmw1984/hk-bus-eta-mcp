#!/usr/bin/env python3
"""
Vercel Serverless Function for HK Transport MCP
使用 Mangum 將 ASGI 應用程式轉換為 Vercel 處理器
"""
import sys
import os
import json

# 添加項目根目錄到 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'src'))

# 初始化 MCP 應用程式
mcp_app = None
initialization_error = None

try:
    from src.server import mcp
    # 使用 SSE transport 創建應用程式
    mcp_app = mcp.http_app(
        transport="sse",
        stateless_http=True
    )
except Exception as e:
    initialization_error = str(e)

# 使用 Mangum 將 ASGI 轉換為 Vercel handler
if mcp_app:
    try:
        from mangum import Mangum
        handler = Mangum(mcp_app, lifespan="off")
    except Exception as e:
        initialization_error = f"Mangum initialization failed: {e}"
        
        # 回退到基本處理器
        from http.server import BaseHTTPRequestHandler
        
        class handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "Handler initialization failed",
                    "details": initialization_error
                }).encode())
else:
    # 如果初始化完全失敗，創建錯誤處理器
    from http.server import BaseHTTPRequestHandler
    
    class handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "MCP initialization failed",
                "details": initialization_error or "Unknown error"
            }).encode())
