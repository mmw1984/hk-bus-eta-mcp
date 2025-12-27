# 快速開始指南

## 本地測試

### 1. 安裝依賴
```bash
pip install -r requirements.txt
```

### 2. 執行伺服器
```bash
python src/server.py
```

伺服器將在 `http://localhost:8000` 啟動。

### 3. 測試功能
```bash
# 測試站點功能
python test_stops.py

# 測試所有功能
python test_all_features.py
```

### 4. 使用 MCP Inspector 測試
```bash
npx @modelcontextprotocol/inspector http://localhost:8000/mcp
```

## 部署到 Vercel

### 方法 1：透過 GitHub
1. 將此專案推送到 GitHub
2. 登入 [Vercel](https://vercel.com)
3. 點擊 "New Project"
4. 選擇你的 GitHub 儲存庫
5. Vercel 會自動檢測 Python 專案並部署

### 方法 2：使用 Vercel CLI
```bash
# 安裝 Vercel CLI
npm install -g vercel

# 部署
vercel
```

## 在 Claude Desktop 中使用

### 1. 找到配置檔案位置

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### 2. 編輯配置檔案

添加以下內容：

```json
{
  "mcpServers": {
    "hk-transport": {
      "url": "https://your-deployment-url.vercel.app/mcp"
    }
  }
}
```

如果使用官方部署：
```json
{
  "mcpServers": {
    "hk-transport": {
      "url": "https://hk-transport-mcp-updated.vercel.app/mcp"
    }
  }
}
```

### 3. 重啟 Claude Desktop

配置更新後，重啟 Claude Desktop 應用程式。

### 4. 開始使用

在 Claude 中嘗試以下問題：
- "幫我查看1號巴士的所有站點"
- "962X路線從哪裡到哪裡？"
- "搜尋旺角附近的巴士站"
- "1號巴士第一個站什麼時候到？"
- "香港今年有哪些公眾假期？"

## 可用的 MCP 工具

伺服器提供 **18 個工具**：

### 路線查詢（4個）
- `search_routes` - 搜尋路線
- `get_route_details` - 路線詳情
- `get_route_stops` - 路線站點
- `get_all_routes` - 所有路線

### ETA 查詢（8個）
- `get_eta` - 通用 ETA
- `get_kmb_eta` - 九巴
- `get_ctb_eta` - 城巴/新巴
- `get_gmb_eta` - 專線小巴
- `get_mtr_eta` - 港鐵
- `get_lightrail_eta` - 輕鐵
- `get_lrtfeeder_eta` - 輕鐵接駁
- `get_nlb_eta` - 新大嶼山巴士

### 站點查詢（5個）
- `search_stops` - 搜尋站點
- `get_stop_info` - 站點資訊
- `get_all_stops` - 所有站點
- `get_stop_mapping` - 站點映射

### 其他（2個）
- `get_holidays` - 公眾假期
- `get_server_info` - 伺服器資訊

## 故障排除

### 問題：伺服器啟動失敗
**解決方案**：
```bash
# 確保已安裝所有依賴
pip install -r requirements.txt

# 檢查 Python 版本（需要 3.11+）
python --version
```

### 問題：Claude Desktop 看不到工具
**解決方案**：
1. 確認配置檔案格式正確（使用 JSON 驗證器）
2. 確認 URL 正確且可訪問
3. 重啟 Claude Desktop
4. 檢查 Claude Desktop 的日誌檔案

### 問題：ETA 資料為空
**解決方案**：
- 某些路線或時段可能沒有即時資料
- 檢查路線 ID 是否正確
- 嘗試使用不同的站點序號

## 更多資訊

- **完整功能說明**: 查看 [FEATURES.md](FEATURES.md)
- **使用範例**: 查看 [USAGE.md](USAGE.md)
- **專案主頁**: [README.md](README.md)

## 技術支援

如遇問題，請：
1. 查看測試腳本範例
2. 閱讀完整文件
3. 檢查錯誤訊息
4. 在 GitHub 提交 Issue
