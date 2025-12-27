#!/usr/bin/env python3
"""
HK Transport MCP Server - Stdio Transport (本地使用)
"""
import sys
from src.server import mcp

if __name__ == "__main__":
    # 使用 stdio transport 運行
    mcp.run(transport="stdio")
