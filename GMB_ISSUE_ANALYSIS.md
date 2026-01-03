# 綠專小巴 (GMB) ETA 問題分析與解決方案

## 問題診斷

### 觀察到的行為
API 返回空數據：
```json
{
  "content": [],
  "structuredContent": {
    "result": []
  },
  "isError": false
}
```

### 根本原因分析

經過測試發現：

#### 1. **直接 `hketa.gmb()` 方法存在問題**
```
KeyError: 'data'
```

這個錯誤表明 `hk-bus-eta` Python 庫的 `gmb()` 方法在處理 API 響應時存在 bug。

#### 2. **正確的方法：使用 `getEtas()` 配合完整的 `route_id`**

✅ **JavaScript 成功案例：**
```javascript
fetchEtas({
  ...busDb.routeList["20+1+San Po Kong+Tsz Wan Shan (North) (Circular)"],
  stopList: busDb.stopList,
  seq: 6,
  language: "zh",
  holidays: busDb.holidays,
  serviceDayMap: busDb.serviceDayMap,
}).then(etas => console.log(etas))
```

✅ **Python 成功案例：**
```python
etas = hketa.getEtas(
    route_id="20+1+San Po Kong+Tsz Wan Shan (North) (Circular)",
    seq=6,
    language="zh"
)
# 返回：
# [
#   {"eta": "2026-01-03T15:09:33.644+08:00", "remark": {...}, "co": "gmb"},
#   {"eta": "2026-01-03T15:35:01.216+08:00", "remark": {...}, "co": "gmb"},
#   ...
# ]
```

## 解決方案（已實施）

### 1. **新增工具：`get_gmb_route_stops`**

幫助用戶找到正確的 GMB 路線 ID 和站點序號：

```python
@mcp.tool(description="獲取綠專小巴路線的站點序號信息")
def get_gmb_route_stops(route_number: str) -> List[Dict[str, Any]]:
    """
    搜索綠專小巴路線並返回所有站點及其序號。
    用於確定 get_eta() 查詢所需的 seq 參數。
    """
```

### 2. **改進 `get_gmb_eta` 函數**

當直接 GMB API 失敗時，自動搜索替代路線並提供使用建議。

### 3. **新增工具：`search_routes_by_operator`**

按營運商搜尋路線：

```python
search_routes_by_operator(operator="gmb", keyword="20")
```

## 正確的使用流程

### 步驟 1：搜索 GMB 路線
```
search_routes_by_operator(operator="gmb", keyword="20")
```

返回：
```json
[
  {
    "route_id": "20+1+San Po Kong+Tsz Wan Shan (North) (Circular)",
    "operators": ["gmb"],
    "origin_zh": "新蒲崗",
    "destination_zh": "慈雲山(北)(循環線)"
  },
  ...
]
```

### 步驟 2：獲取站點序號
```
get_gmb_route_stops(route_number="20")
```

返回：
```json
{
  "route_id": "20+1+San Po Kong+Tsz Wan Shan (North) (Circular)",
  "stops": [
    {"seq": 0, "stop_id": "...", "name_zh": "新蒲崗"},
    {"seq": 1, "stop_id": "...", "name_zh": "..."},
    {"seq": 6, "stop_id": "...", "name_zh": "聖母醫院"},
    ...
  ],
  "usage_example": "get_eta(route_id='20+1+San Po Kong+...', seq=站點序號, language='zh')"
}
```

### 步驟 3：獲取 ETA
```
get_eta(
    route_id="20+1+San Po Kong+Tsz Wan Shan (North) (Circular)",
    seq=6,
    language="zh"
)
```

返回：
```json
[
  {
    "eta": "2026-01-03T15:09:33.644+08:00",
    "remark": {"zh": null, "en": null},
    "co": "gmb"
  },
  {
    "eta": "2026-01-03T15:35:01.216+08:00",
    "remark": {"zh": "未開出", "en": "Scheduled"},
    "co": "gmb"
  }
]
```

## 關鍵發現

| 方法 | 狀態 | 說明 |
|------|------|------|
| `hketa.gmb(gtfs_id=..., stop_id=...)` | ❌ 失敗 | 拋出 KeyError: 'data' |
| `hketa.getEtas(route_id=..., seq=...)` | ✅ 成功 | 正確返回 ETA 數據 |

## 重要參數

- **`route_id`**：必須使用完整格式，如 `"20+1+San Po Kong+Tsz Wan Shan (North) (Circular)"`
- **`seq`**：站點序號，從 0 開始計算，必須與路線的站點列表對應

## 測試驗證

```bash
# 測試 GMB ETA 查詢
python -c "
from hk_bus_eta import HKEta
h = HKEta()
etas = h.getEtas(
    route_id='20+1+San Po Kong+Tsz Wan Shan (North) (Circular)',
    seq=6,
    language='zh'
)
print(f'獲得 {len(etas)} 個 ETA')
for eta in etas:
    print(eta)
"
```

## 結論

**問題根源**：`hketa.gmb()` 方法存在 bug，無法正確處理 API 響應。

**解決方案**：使用 `hketa.getEtas(route_id=完整路線ID, seq=站點序號)` 通用方法。

**新增工具**：
1. `get_gmb_route_stops(route_number)` - 獲取 GMB 路線的站點序號
2. `search_routes_by_operator(operator, keyword)` - 按營運商搜尋路線

**用戶體驗改進**：
- 當直接 GMB API 失敗時，自動提供替代方案和使用示例
- 更清晰的錯誤信息和建議
