# 香港交通 ETA MCP 伺服器

這是一個模型上下文協議（MCP）伺服器，提供香港公共交通的即時預計到達時間（ETA）。它使用 [FastMCP](https://github.com/jlowin/fastmcp) 框架和 [hk-bus-eta](https://github.com/hkbus/hk-bus-eta) 庫構建。

## 功能特色

- **搜尋路線**：使用關鍵字查找路線 ID（例如："962X"、"TCL"）。
- **獲取 ETA**：獲取特定路線和站點的即時到達時間。
- **路線詳情**：獲取路線的詳細資訊，包括其站點。
- **路線站點**：獲取路線的所有站點及其中英文名稱。
- **多營運商支援**：支援九巴（KMB）、城巴/新巴（CTB）、專線小巴（GMB）、港鐵（MTR）、輕鐵（Light Rail）、輕鐵接駁巴士（LRT Feeder）、新大嶼山巴士（NLB）。
- **站點搜尋**：根據名稱搜尋站點。
- **假期資訊**：獲取香港公眾假期列表。

## 工具列表

### 路線相關
- `search_routes(keyword: str)` - 搜尋路線 ID
- `get_route_details(route_id: str)` - 獲取路線資訊
- `get_route_stops(route_id: str, language: str)` - 獲取所有站點及其名稱和位置
- `get_all_routes()` - 獲取所有可用路線列表

### ETA 查詢（通用）
- `get_eta(route_id: str, seq: int, language: str)` - 獲取即時 ETA

### ETA 查詢（各營運商）
- `get_kmb_eta(stop_id, route, service_type, bound)` - 九巴 ETA
- `get_ctb_eta(stop_id, route, bound, seq)` - 城巴/新巴 ETA
- `get_gmb_eta(gtfs_id, stop_id, bound, seq)` - 專線小巴 ETA
- `get_mtr_eta(stop_id, route, bound)` - 港鐵 ETA
- `get_lightrail_eta(stop_id, route, dest)` - 輕鐵 ETA
- `get_lrtfeeder_eta(stop_id, route, language)` - 輕鐵接駁巴士 ETA
- `get_nlb_eta(stop_id, nlb_id)` - 新大嶼山巴士 ETA

### 站點相關
- `search_stops(keyword: str, language: str)` - 搜尋站點
- `get_stop_info(stop_id: str)` - 獲取站點詳細資訊
- `get_all_stops()` - 獲取所有站點列表
- `get_stop_mapping(stop_id: str)` - 獲取站點在不同營運商之間的映射

### 其他
- `get_holidays()` - 獲取香港公眾假期列表
- `get_server_info()` - 獲取伺服器元數據

## 部署

### Vercel

此專案已配置為可在 Vercel 上部署。

要部署您自己的實例：
1. Fork 此儲存庫
2. 將其匯入到 Vercel
3. Vercel 將自動部署為 Python 無伺服器函數

在 Claude Desktop 中使用，請將以下內容添加到您的配置：
```json
{
  "mcpServers": {
    "hk-transport": {
      "url": "https://hk-transport-mcp-updated.vercel.app/mcp"
    }
  }
}
```

### 本地開發

1. 安裝依賴套件：
   ```bash
   pip install -r requirements.txt
   ```

2. 執行伺服器：
   ```bash
   python src/server.py
   ```

3. 使用 MCP Inspector 測試：
   ```bash
   npx @modelcontextprotocol/inspector http://localhost:8000/mcp
   ```

## 致謝

- 數據由 [data.gov.hk](https://data.gov.hk) 提供。
- 由 [hkbus.app](https://github.com/hkbus) 標準化。
- 使用 [FastMCP](https://github.com/jlowin/fastmcp) 構建。
- 模板由 [Interaction Company of California](https://github.com/InteractionCo) 提供。

