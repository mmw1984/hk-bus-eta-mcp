# 香港交通 ETA MCP 伺服器 - 完整功能說明

## 版本資訊
- **版本**: 2.0.0
- **最後更新**: 2025年12月27日
- **支援營運商**: KMB、CTB、GMB、MTR、Light Rail、LRT Feeder、NLB

## 完整功能列表（18個工具）

### 📍 路線相關（4個工具）

#### 1. `search_routes(keyword: str)` 
搜尋香港巴士或交通路線 ID

**參數**：
- `keyword`: 搜尋關鍵字（例如："1"、"962X"、"TCL"）

**返回**：符合條件的路線 ID 列表（最多20個）

**範例**：
```python
search_routes("962")
# 返回: ['962+1+GOLD COAST+CENTRAL (EXCHANGE SQUARE)', ...]
```

---

#### 2. `get_route_details(route_id: str)`
獲取特定路線的詳細資料

**參數**：
- `route_id`: 路線的唯一識別碼

**返回**：包含起點、終點、營運商、站點、車費等完整路線資訊

**範例**：
```python
get_route_details("1+1+CHUK YUEN ESTATE+STAR FERRY")
```

---

#### 3. `get_route_stops(route_id: str, language: str = "en")`
獲取路線的所有站點及其名稱和序號

**參數**：
- `route_id`: 路線的唯一識別碼
- `language`: 站點名稱語言（"en" 或 "zh"，預設為 "en"）

**返回**：站點列表，包含序號、站點名稱（中英文）、位置、營運商

**範例**：
```python
get_route_stops("1+1+CHUK YUEN ESTATE+STAR FERRY", language="zh")
```

---

#### 4. `get_all_routes()`
獲取所有可用的路線列表

**返回**：總路線數及前50個路線 ID 範例

---

### 🕒 ETA 查詢（8個工具）

#### 5. `get_eta(route_id: str, seq: int = 0, language: str = "en")`
獲取香港交通路線特定站點的預計到達時間（通用）

**參數**：
- `route_id`: 路線的唯一識別碼
- `seq`: 站點序號（預設為 0，即第一個站點）
- `language`: 備註語言（"en" 或 "zh"）

**返回**：ETA 列表，包含預計到達時間、備註等

---

#### 6. `get_kmb_eta(stop_id: str, route: str, service_type: str = "1", bound: str = "O")`
獲取九巴（KMB）特定站點的 ETA

**參數**：
- `stop_id`: 站點 ID
- `route`: 路線編號
- `service_type`: 服務類型（預設為 "1"）
- `bound`: 方向（"O" 為去程，"I" 為回程）

---

#### 7. `get_ctb_eta(stop_id: str, route: str, bound: str = "outbound", seq: int = 0)`
獲取城巴/新巴（CTB）特定站點的 ETA

**參數**：
- `stop_id`: 站點 ID
- `route`: 路線編號
- `bound`: 方向（"outbound" 或 "inbound"）
- `seq`: 站點序號

---

#### 8. `get_gmb_eta(gtfs_id: str, stop_id: str, bound: str = "1", seq: int = 0)`
獲取專線小巴（GMB）特定站點的 ETA

**參數**：
- `gtfs_id`: GTFS 路線 ID
- `stop_id`: 站點 ID
- `bound`: 方向
- `seq`: 站點序號

---

#### 9. `get_mtr_eta(stop_id: str, route: str, bound: str = "1")`
獲取港鐵（MTR）特定站點的 ETA

**參數**：
- `stop_id`: 站點 ID
- `route`: 路線編號
- `bound`: 方向

---

#### 10. `get_lightrail_eta(stop_id: str, route: str, dest: str = "")`
獲取輕鐵（Light Rail）特定站點的 ETA

**參數**：
- `stop_id`: 站點 ID
- `route`: 路線編號
- `dest`: 目的地

---

#### 11. `get_lrtfeeder_eta(stop_id: str, route: str, language: str = "en")`
獲取輕鐵接駁巴士特定站點的 ETA

**參數**：
- `stop_id`: 站點 ID
- `route`: 路線編號
- `language`: 語言（"en" 或 "zh"）

---

#### 12. `get_nlb_eta(stop_id: str, nlb_id: str)`
獲取新大嶼山巴士（NLB）特定站點的 ETA

**參數**：
- `stop_id`: 站點 ID
- `nlb_id`: NLB 路線 ID

---

### 🚏 站點相關（5個工具）

#### 13. `search_stops(keyword: str, language: str = "en")`
根據關鍵字搜尋站點

**參數**：
- `keyword`: 搜尋關鍵字
- `language`: 搜尋語言（"en" 或 "zh"）

**返回**：符合條件的站點列表（最多20個），包含站點名稱（中英文）和位置

**範例**：
```python
search_stops("旺角", language="zh")
```

---

#### 14. `get_stop_info(stop_id: str)`
獲取特定站點的詳細資訊

**參數**：
- `stop_id`: 站點 ID

**返回**：站點的完整資訊，包括名稱（中英文）和地理位置

---

#### 15. `get_all_stops()`
獲取所有可用的站點列表

**返回**：總站點數及前50個站點 ID 範例

---

#### 16. `get_stop_mapping(stop_id: str)`
獲取站點在不同營運商之間的映射關係

**參數**：
- `stop_id`: 站點 ID

**返回**：站點在各營運商的對應資訊

**用途**：了解同一物理位置在不同營運商系統中的站點 ID

---

### 📅 其他功能（2個工具）

#### 17. `get_holidays()`
獲取香港公眾假期列表

**返回**：假期日期列表（格式：YYYYMMDD）

**範例輸出**：
```python
['20240101', '20240210', '20240212', ...]
```

---

#### 18. `get_server_info()`
獲取 MCP 伺服器的資訊

**返回**：伺服器名稱、版本、支援的營運商、路線和站點統計等

---

## 數據統計

截至最後更新：
- **總路線數**: 3,752 條
- **總站點數**: 15,227 個
- **站點映射**: 11,891 個
- **公眾假期**: 51 個

### 各營運商路線數：
- KMB（九巴）: 1,607 條
- GMB（專線小巴）: 1,153 條
- CTB（城巴/新巴）: 950 條
- NLB（新大嶼山巴士）: 99 條
- LRTFeeder（輕鐵接駁）: 63 條
- MTR（港鐵）: 24 條
- LightRail（輕鐵）: 20 條
- 其他渡輪: 29 條

## 使用建議

1. **搜尋流程**：先使用 `search_routes()` 找到路線 ID，再使用其他工具查詢詳細資訊
2. **語言設定**：繁體中文使用 `language="zh"`，英文使用 `language="en"`
3. **站點序號**：從 0 開始，0 代表第一個站點
4. **錯誤處理**：所有工具都會在出錯時返回包含 "error" 鍵的字典

## 技術規格

- **框架**: FastMCP
- **數據來源**: hk-bus-eta（整合 data.gov.hk 和 hkbus.app）
- **協議**: MCP (Model Context Protocol)
- **部署**: Vercel（無伺服器函數）
- **語言**: Python 3.11+

## 聯絡資訊

- **作者**: Manus AI
- **GitHub**: https://github.com/InteractionCo
- **數據提供**: data.gov.hk, hkbus.app
