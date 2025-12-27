#!/usr/bin/env python3
"""
調試端點 - 用於診斷 Vercel 構建問題
"""
from http.server import BaseHTTPRequestHandler
import json
import sys
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # 收集診斷信息
        debug_info = {
            "python_version": sys.version,
            "platform": sys.platform,
            "cwd": os.getcwd(),
            "path": sys.path[:5],  # 只顯示前5個路徑
            "api_dir_exists": os.path.exists("/var/task/api"),
            "src_dir_exists": os.path.exists("/var/task/src"),
            "lib_dir_exists": os.path.exists("/var/task/lib"),
            "imports": {}
        }
        
        # 嘗試導入各個模塊
        try:
            import fastmcp
            debug_info["imports"]["fastmcp"] = str(fastmcp.__version__ if hasattr(fastmcp, '__version__') else "installed")
        except Exception as e:
            debug_info["imports"]["fastmcp"] = f"error: {str(e)}"
        
        try:
            import hk_bus_eta
            debug_info["imports"]["hk_bus_eta"] = "installed"
        except Exception as e:
            debug_info["imports"]["hk_bus_eta"] = f"error: {str(e)}"
        
        try:
            import starlette
            debug_info["imports"]["starlette"] = "installed"
        except Exception as e:
            debug_info["imports"]["starlette"] = f"error: {str(e)}"
        
        # 嘗試導入 src.server
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            sys.path.insert(0, parent_dir)
            sys.path.insert(0, os.path.join(parent_dir, 'src'))
            
            from src.server import mcp
            debug_info["imports"]["src.server"] = "success"
            debug_info["mcp_name"] = mcp.name if hasattr(mcp, 'name') else "unknown"
        except Exception as e:
            debug_info["imports"]["src.server"] = f"error: {str(e)}"
        
        self.wfile.write(json.dumps(debug_info, indent=2).encode())
        return
