# 優化的 ETA 查詢工作流程

## 新增功能

本次更新新增了三個工具，大幅簡化 ETA 查詢流程：

### 1. 增強的路線搜尋：`search_routes`

**改進內容：**
- 每個路線方向作為獨立條目顯示
- 包含營運商資訊（支援 KMB、CTB、GMB、MTR、NLB 等所有營運商）
- 可選參數：按營運商過濾
- 返回可直接用於後續查詢的 `route_id`

**使用範例：**
```python
# 搜尋所有路線 1
search_routes(keyword="1")

# 搜尋所有九巴路線 1
search_routes(keyword="1", operator="kmb")

# 搜尋所有小巴路線
search_routes(operator="gmb")
```

**返回格式：**
```json
[
  {
    "route_id": "1+1+CHUK YUEN ESTATE+STAR FERRY",
    "route_number": "1",
    "operators": ["kmb"],
    "origin_zh": "竹園邨",
    "destination_zh": "尖沙咀碼頭",
    "origin_en": "Chuk Yuen Estate",
    "destination_en": "Star Ferry",
    "description": "1 (kmb) 竹園邨 → 尖沙咀碼頭"
  }
]
```

### 2. 路線站點查詢：`get_route_stops`

**功能：**
- 獲取任何路線的所有站點列表
- 支援所有營運商（KMB、CTB、GMB、MTR、NLB 等）
- 包含站點名稱、序號、位置資訊
- 按站點順序排列

**使用範例：**
```python
# 獲取小巴 20 號的所有站點（中文）
get_route_stops(route_id="20+1+San Po Kong+Tsz Wan Shan (North) (Circular)", language="zh")

# 獲取九巴 1 號的所有站點（英文）
get_route_stops(route_id="1+1+CHUK YUEN ESTATE+STAR FERRY", language="en")
```

**返回格式：**
```json
{
  "route_id": "20+1+San Po Kong+Tsz Wan Shan (North) (Circular)",
  "operators": ["gmb"],
  "origin": "新蒲崗",
  "destination": "慈雲山 (北) (循環線)",
  "stops_count": 25,
  "stops": [
    {
      "seq": 0,
      "stop_id": "20012703",
      "name": "康強街, 近安強大樓",
      "name_zh": "康強街, 近安強大樓",
      "name_en": "Hong Keung Street, near On Keung Building",
      "location": {"lat": 22.334567, "lng": 114.198765},
      "operator": "gmb"
    }
  ]
}
```

### 3. 批量 ETA 查詢：`get_route_all_stops_eta`

**功能：**
- 一次性獲取路線所有站點的 ETA
- 按站點順序排列，方便查看整條路線的班次情況
- 自動統計有 ETA 數據的站點數量
- 支援所有營運商

**使用範例：**
```python
# 獲取小巴 20 號所有站點的 ETA（中文）
get_route_all_stops_eta(route_id="20+1+San Po Kong+Tsz Wan Shan (North) (Circular)", language="zh")

# 獲取九巴 1 號所有站點的 ETA（英文）
get_route_all_stops_eta(route_id="1+1+CHUK YUEN ESTATE+STAR FERRY", language="en")
```

**返回格式：**
```json
{
  "route_id": "20+1+San Po Kong+Tsz Wan Shan (North) (Circular)",
  "operators": ["gmb"],
  "origin": "新蒲崗",
  "destination": "慈雲山 (北) (循環線)",
  "total_stops": 25,
  "stops_with_eta": 25,
  "language": "zh",
  "stops_eta": [
    {
      "seq": 0,
      "stop_id": "20012703",
      "stop_name": "康強街, 近安強大樓",
      "has_eta": true,
      "operator": "gmb",
      "etas": [
        {
          "time": "2026-01-03T15:40:00.000+08:00",
          "remark": "未開出",
          "operator": "gmb",
          "destination": "慈雲山 (北) (循環線)"
        },
        {
          "time": "2026-01-03T15:55:00.000+08:00",
          "remark": "未開出",
          "operator": "gmb",
          "destination": "慈雲山 (北) (循環線)"
        }
      ]
    }
  ]
}
```

## 優化的工作流程

### 完整查詢流程

```
1. 搜尋路線
   ↓
   search_routes(keyword="20")
   → 返回所有包含 "20" 的路線，每個方向獨立顯示

2. 選擇路線，查看所有站點
   ↓
   get_route_stops(route_id="20+1+San Po Kong+Tsz Wan Shan (North) (Circular)")
   → 返回該路線所有站點列表

3. 一次性查詢所有站點 ETA
   ↓
   get_route_all_stops_eta(route_id="20+1+San Po Kong+Tsz Wan Shan (North) (Circular)")
   → 返回該路線所有站點的即時 ETA
```

### 快捷流程（直接查詢所有站點 ETA）

如果已知路線編號：

```
search_routes(keyword="20") → 獲取 route_id
         ↓
get_route_all_stops_eta(route_id="...") → 一次獲取所有 ETA
```

### 按營運商過濾

```python
# 只搜尋小巴路線
search_routes(keyword="20", operator="gmb")

# 只搜尋九巴路線
search_routes(keyword="1", operator="kmb")

# 只搜尋城巴路線
search_routes(keyword="962", operator="ctb")
```

## 實際使用案例

### 案例 1：查詢小巴 20 號所有站點的班次

```python
# 步驟 1: 搜尋路線
routes = search_routes(keyword="20", operator="gmb")
# 找到: "20+1+San Po Kong+Tsz Wan Shan (North) (Circular)"

# 步驟 2: 直接獲取所有站點 ETA
all_eta = get_route_all_stops_eta(
    route_id="20+1+San Po Kong+Tsz Wan Shan (North) (Circular)",
    language="zh"
)

# 結果：25 個站點的所有 ETA 數據
# - total_stops: 25
# - stops_with_eta: 25
# - 每個站點包含多個預測到達時間
```

### 案例 2：查看九巴 1 號的路線結構

```python
# 步驟 1: 搜尋路線（可能有多個方向）
routes = search_routes(keyword="1", operator="kmb")

# 步驟 2: 選擇方向後查看站點
stops = get_route_stops(
    route_id="1+1+CHUK YUEN ESTATE+STAR FERRY",
    language="en"
)

# 結果：顯示從竹園邨到尖沙咀碼頭方向的所有站點
```

### 案例 3：比較不同營運商的同號路線

```python
# 搜尋所有路線 1（包括 KMB、CTB、GMB）
all_route_1 = search_routes(keyword="1")

# 分別查詢各營運商的 ETA
kmb_1_eta = get_route_all_stops_eta(route_id="1+1+CHUK YUEN ESTATE+STAR FERRY")
ctb_1_eta = get_route_all_stops_eta(route_id="1+1+Central (Macau Ferry)+Happy Valley (Upper)")
gmb_1_eta = get_route_all_stops_eta(route_id="1+1+Central (Hong Kong Station Public Transport Interchange)+The Peak (Public Transport Terminus)")
```

## 效能與限制

### 效能考慮
- `search_routes`: 快速（僅搜尋本地數據），限制返回 100 條路線
- `get_route_stops`: 快速（僅讀取本地數據）
- `get_route_all_stops_eta`: 較慢（需查詢每個站點的即時 ETA）
  - 每個站點約需 0.5-1 秒
  - 25 個站點的路線約需 12-25 秒

### 建議
- 對於長路線（> 30 站），建議先使用 `get_route_stops` 查看站點列表
- 如只需查詢特定站點，使用 `get_eta(route_id, seq, language)` 會更快
- `get_route_all_stops_eta` 適合需要查看整條路線班次分佈的場景

## 向後兼容性

### 已棄用的工具
- `get_gmb_route_stops`: 建議改用 `get_route_stops`（支援所有營運商）

### 現有工具仍然可用
- `get_eta`: 查詢單一站點 ETA
- `search_routes_by_operator`: 按營運商搜尋路線
- `get_gmb_eta`, `get_kmb_eta`, `get_ctb_eta` 等：特定營運商的 ETA 查詢

## 測試

執行測試腳本驗證功能：

```bash
python test_new_tools.py
```

測試內容包括：
1. 搜尋路線功能
2. 獲取路線站點
3. 批量查詢 ETA（前 3 個站點）

---

**更新日期：** 2026-01-03  
**版本：** 2.2.0
