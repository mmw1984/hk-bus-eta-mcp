# HK Bus ETA MCP

香港交通 ETA 的 MCP 伺服器（FastMCP + hk-bus-eta）。

本版本重點：
- 移除不必要與重複代碼。
- 工具命名改為「一語言一工具」（`_zh` / `_en`）。
- API 以簡單、低參數、快速回應為優先。

## 快速開始

```bash
pip install -r requirements.txt
python src/server.py
```

本地 MCP 端點：`http://localhost:8000/mcp`

## 設計原則

- 語言分離：中文與英文使用不同工具，避免 `language` 參數混淆。
- 快速回應：搜尋與批量工具都有 `limit` 或 `max_stops` 上限。
- 明確命名：工具名稱直接表達用途，不需要閱讀長文檔才能用。

## 工具總覽

### 路線搜尋
- `search_routes_zh(keyword="", operator="", limit=50)`
- `search_routes_en(keyword="", operator="", limit=50)`
- `search_routes_by_operator_zh(operator="gmb", keyword="", limit=50)`
- `search_routes_by_operator_en(operator="gmb", keyword="", limit=50)`
- `find_route_ids_by_number(route_number, operator="", limit=20)`

### ETA（通用）
- `get_eta_zh(route_id, seq=0)`
- `get_eta_en(route_id, seq=0)`

### 路線站點
- `get_route_stops_zh(route_id, limit=9999)`
- `get_route_stops_en(route_id, limit=9999)`
- `get_route_all_stops_eta_zh(route_id, max_stops=20)`
- `get_route_all_stops_eta_en(route_id, max_stops=20)`

### 站點搜尋
- `search_stops_zh(keyword, limit=20)`
- `search_stops_en(keyword, limit=20)`

### 營運商專用 ETA
- `get_kmb_eta(stop_id, route, service_type="1", bound="O")`
- `get_ctb_eta(stop_id, route, bound="outbound", seq=0)`
- `get_gmb_eta(gtfs_id, stop_id, bound="1", seq=0)`
- `get_mtr_eta(stop_id, route, bound="1")`
- `get_lightrail_eta(stop_id, route, dest_zh="", dest_en="")`
- `get_lrtfeeder_eta_zh(stop_id, route)`
- `get_lrtfeeder_eta_en(stop_id, route)`
- `get_nlb_eta(stop_id, nlb_id)`

### 其他資料工具
- `get_route_details(route_id)`
- `get_all_routes(limit=50)`
- `get_all_stops(limit=50)`
- `get_stop_info(stop_id)`
- `get_stop_mapping(stop_id)`
- `get_holidays()`
- `get_server_info()`

## 建議工作流

1. 用 `search_routes_zh` 或 `find_route_ids_by_number` 找 `route_id`。
2. 用 `get_route_stops_zh` 看站序（`seq`）。
3. 用 `get_eta_zh(route_id, seq)` 查單站 ETA。
4. 若要快速總覽，用 `get_route_all_stops_eta_zh(route_id, max_stops=20)`。

## Streaming 端點

- `/stream`：SSE 單路線串流
- `/batch`：SSE 批量/附近站點/Live 更新

詳見：`STREAMING_API.md`

## 部署

- Vercel：已包含 `api/mcp.py`、`api/stream.py`、`api/batch_stream.py`。
- 若要接 Claude Desktop，將伺服器 URL 指向 `/mcp`。
