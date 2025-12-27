#!/usr/bin/env python3
"""
Vercel Serverless Function for HK Transport MCP
"""
import sys
import os

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from server import app

# Vercel 需要這個變數
handler = app
