# 使用範例

## 1. 搜尋路線

```python
from server import search_routes

# 搜尋包含 "1" 的路線
routes = search_routes("1")
print(routes)
# ['1+1+CHUK YUEN ESTATE+STAR FERRY', '1+2+STAR FERRY+CHUK YUEN ESTATE', ...]
```

## 2. 獲取路線站點名稱

```python
from server import get_route_stops

# 獲取1號巴士的所有站點（英文）
stops = get_route_stops('1+1+CHUK YUEN ESTATE+STAR FERRY', language='en')
for stop in stops:
    print(f"{stop['seq']}. {stop['name']}")

# 獲取站點（中文）
stops_zh = get_route_stops('1+1+CHUK YUEN ESTATE+STAR FERRY', language='zh')
for stop in stops_zh:
    print(f"{stop['seq']}. {stop['name']}")
```

輸出範例：
```
0. CHUK YUEN ESTATE BUS TERMINUS (WT916)
1. RAINBOW PRIMARY SCHOOL (WT418)
2. MA CHAI HANG RECREATION GROUND (WT426)
3. MORSE PARK (WT105)
...
```

## 3. 獲取即時到站時間

```python
from server import get_eta

# 獲取第一個站點的到站時間
etas = get_eta('1+1+CHUK YUEN ESTATE+STAR FERRY', seq=0, language='en')
print(etas)
```

## 4. 獲取路線詳細資訊

```python
from server import get_route_details

# 獲取路線的原始數據
route_info = get_route_details('1+1+CHUK YUEN ESTATE+STAR FERRY')
print(f"起點: {route_info['orig']['zh']}")
print(f"終點: {route_info['dest']['zh']}")
print(f"車費: {route_info['fares'][0]} HKD")
```

## 5. 搜尋站點

```python
from server import search_stops

# 搜尋包含 "旺角" 的站點
stops = search_stops("旺角", language="zh")
for stop in stops:
    print(f"{stop['name_zh']} ({stop['name_en']})")
```

## 6. 獲取各營運商的 ETA

### 九巴（KMB）
```python
from server import get_kmb_eta

# 獲取九巴特定站點的 ETA
etas = get_kmb_eta(stop_id="18492910339410B1", route="1", bound="O")
print(etas)
```

### 港鐵（MTR）
```python
from server import get_mtr_eta

# 獲取港鐵特定站點的 ETA
etas = get_mtr_eta(stop_id="TST", route="TML", bound="1")
print(etas)
```

## 7. 獲取香港公眾假期

```python
from server import get_holidays

# 獲取假期列表
holidays = get_holidays()
print(holidays)
# ['20240101', '20240210', '20240212', ...]
```

## 8. 獲取站點映射資訊

```python
from server import get_stop_mapping

# 獲取站點在不同營運商之間的映射
mapping = get_stop_mapping("00040ED8B61CA94B")
print(mapping)
```

## MCP 客戶端使用

在 Claude Desktop 配置檔案中添加：

```json
{
  "mcpServers": {
    "hk-transport": {
      "url": "https://hk-transport-mcp-updated.vercel.app/mcp"
    }
  }
}
```

然後在 Claude 中可以直接詢問：
- "幫我查看1號巴士的所有站點名稱"
- "962X路線有哪些站?"
- "1號巴士第5個站點什麼時候到?"
- "搜尋旺角附近的巴士站"
- "香港有哪些公眾假期?"

## 新功能特性

### get_route_stops() 返回的數據結構：

```json
[
  {
    "seq": 0,
    "stop_id": "18492910339410B1",
    "name": "CHUK YUEN ESTATE BUS TERMINUS (WT916)",
    "name_en": "CHUK YUEN ESTATE BUS TERMINUS (WT916)",
    "name_zh": "竹園邨總站 (WT916)",
    "location": {
      "lat": 22.34541,
      "lng": 114.19264
    },
    "company": "kmb"
  },
  ...
]
```

### 支援的語言：
- `en`: 英文站名
- `zh`: 繁體中文站名

### 包含的資訊：
- 站點序號（seq）
- 站點ID（stop_id）
- 站點名稱（name、name_en、name_zh）
- 地理位置（location）
- 營運公司（company）

## 完整功能列表

### 所有可用的 MCP 工具：

1. **路線相關**
   - `search_routes` - 搜尋路線
   - `get_route_details` - 獲取路線詳情
   - `get_route_stops` - 獲取路線站點
   - `get_all_routes` - 列出所有路線

2. **ETA 查詢**
   - `get_eta` - 通用 ETA 查詢
   - `get_kmb_eta` - 九巴 ETA
   - `get_ctb_eta` - 城巴/新巴 ETA
   - `get_gmb_eta` - 專線小巴 ETA
   - `get_mtr_eta` - 港鐵 ETA
   - `get_lightrail_eta` - 輕鐵 ETA
   - `get_lrtfeeder_eta` - 輕鐵接駁巴士 ETA
   - `get_nlb_eta` - 新大嶼山巴士 ETA

3. **站點相關**
   - `search_stops` - 搜尋站點
   - `get_stop_info` - 獲取站點資訊
   - `get_all_stops` - 列出所有站點
   - `get_stop_mapping` - 獲取站點映射

4. **其他功能**
   - `get_holidays` - 獲取公眾假期
   - `get_server_info` - 獲取伺服器資訊

## 支援的營運商

- **KMB** - 九龍巴士
- **CTB** - 城巴
- **NWFB** - 新世界第一巴士
- **GMB** - 專線小巴
- **MTR** - 港鐵
- **Light Rail** - 輕鐵
- **LRT Feeder** - 輕鐵接駁巴士
- **NLB** - 新大嶼山巴士
