#!/usr/bin/env python3
"""
調試版本 - 檢查導入問題
"""
from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import traceback

# 添加項目根目錄到 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'src'))

# 嘗試導入並記錄錯誤
error_msg = None
try:
    from src.server import mcp
    mcp_loaded = True
except Exception as e:
    mcp_loaded = False
    error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200 if mcp_loaded else 500)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "mcp_loaded": mcp_loaded,
            "python_version": sys.version,
            "sys_path": sys.path[:5],
            "error": error_msg if not mcp_loaded else None
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode())
