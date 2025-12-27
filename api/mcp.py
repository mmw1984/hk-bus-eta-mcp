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

try:
    from src.server import app
except ImportError:
    from server import app

# Vercel 需要這個變數
handler = app
