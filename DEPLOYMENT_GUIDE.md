# HK Transport MCP 部署指南

## 問題診斷

經過分析，發現 **Vercel 不適合部署 FastMCP HTTP/SSE 服務器**：

1. **時間限制**：Vercel Serverless Functions 有執行時間限制
   - 免費版：10 秒
   - 付費版：60 秒
   
2. **不支持長連接**：FastMCP 的 HTTP/SSE 傳輸需要長時間保持連接，而 Vercel 會在超時後強制斷開

3. **構建問題**：`api/mcp.py` 在 Vercel 構建時失敗，導致只有 `api/index` 被部署

## 推薦解決方案

### 方案 A：本地運行（最簡單）✅

MCP 協議主要設計為本地使用。使用 stdio 傳輸在本地運行：

1. **配置 Claude Desktop 或其他 MCP 客戶端**

在 Claude Desktop 配置文件中添加（通常在 `%APPDATA%\Claude\claude_desktop_config.json`）：

\`\`\`json
{
  "mcpServers": {
    "hk-transport": {
      "command": "python",
      "args": ["-m", "run_local"],
      "cwd": "c:\\Users\\mmw1984\\Downloads\\hk-transport-mcp-updated"
    }
  }
}
\`\`\`

2. **直接運行（測試）**

\`\`\`powershell
cd c:\Users\mmw1984\Downloads\hk-transport-mcp-updated
python run_local.py
\`\`\`

**優點**：
- ✅ 無需部署
- ✅ 無連接超時問題
- ✅ 數據保持在本地
- ✅ 響應速度快

**缺點**：
- ❌ 需要本地 Python 環境
- ❌ 無法遠程訪問

### 方案 B：使用支持長連接的平台

如果您確實需要遠程部署，推薦使用：

#### 1. **Railway** （推薦）

\`\`\`bash
# 安裝 Railway CLI
npm install -g @railway/cli

# 登入
railway login

# 初始化並部署
cd c:\Users\mmw1984\Downloads\hk-transport-mcp-updated
railway init
railway up
\`\`\`

創建 `Procfile`:
\`\`\`
web: python -m src.server --port $PORT --host 0.0.0.0
\`\`\`

#### 2. **Render**

在 Render 上創建新的 Web Service，使用以下設置：
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python -m src.server --port $PORT --host 0.0.0.0`

#### 3. **Fly.io**

\`\`\`bash
# 安裝 flyctl
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

# 登入並部署
cd c:\Users\mmw1984\Downloads\hk-transport-mcp-updated
fly launch
fly deploy
\`\`\`

### 方案 C：重構為 API 端點（不推薦）

可以將 MCP 工具重構為簡單的 REST API，但會失去 MCP 協議的優勢。

## Vercel 部署問題詳情

### 構建日誌分析

從 Vercel 部署日誌可以看到：
- ✅ 構建成功：`Build Completed in /vercel/output [5s]`
- ✅ `api/index.py` 被部署（健康檢查端點）
- ✅ `api/test.py` 被部署（測試端點）
- ❌ `api/mcp.py` **未被部署**（構建時失敗）

### 為何 `api/mcp.py` 失敗

1. **Mangum 適配器問題**：Vercel 的 Python runtime 可能與 Mangum (ASGI->AWS Lambda 適配器) 不完全兼容
2. **FastMCP ASGI 應用**：FastMCP 的 `http_app()` 返回 Starlette (ASGI) 應用，而 Vercel Python runtime 期望簡單的處理器類
3. **導入失敗**：在構建時如果導入失敗，Vercel 會跳過該文件

## 下一步

**建議**：使用方案 A（本地運行），因為：
1. MCP 主要為本地客戶端設計
2. 無需處理部署和連接問題
3. 響應更快，更可靠

如果您確實需要遠程訪問，可以嘗試方案 B 中的 Railway 或 Render。
