#!/usr/bin/env python3
"""測試所有 hk_bus_eta 功能"""

from hk_bus_eta import HKEta
import json

print("=" * 80)
print("香港交通 ETA 功能測試")
print("=" * 80)

print("\n正在初始化 HKEta...")
hketa = HKEta()
print("✓ 初始化完成")

# 1. 測試搜尋路線
print("\n" + "=" * 80)
print("1. 測試搜尋路線")
print("=" * 80)
keyword = "1"
routes = [r for r in hketa.route_list.keys() if keyword in r][:5]
print(f"搜尋關鍵字 '{keyword}' 的前 5 個結果:")
for route in routes:
    print(f"  - {route}")

# 2. 測試獲取路線詳情
print("\n" + "=" * 80)
print("2. 測試獲取路線詳情")
print("=" * 80)
if routes:
    route_id = routes[0]
    route_info = hketa.route_list.get(route_id)
    print(f"路線 ID: {route_id}")
    print(f"起點: {route_info['orig']['zh']} ({route_info['orig']['en']})")
    print(f"終點: {route_info['dest']['zh']} ({route_info['dest']['en']})")
    print(f"營運商: {', '.join(route_info['co'])}")
    print(f"站點數量: {route_info['seq']}")

# 3. 測試獲取路線站點
print("\n" + "=" * 80)
print("3. 測試獲取路線站點")
print("=" * 80)
if routes:
    route_id = routes[0]
    route_info = hketa.route_list.get(route_id)
    print(f"路線 {route_id} 的前 5 個站點:")
    for company, stop_ids in route_info.get("stops", {}).items():
        print(f"\n營運商: {company.upper()}")
        for idx, stop_id in enumerate(stop_ids[:5]):
            stop_info = hketa.stop_list.get(stop_id)
            if stop_info:
                print(f"  {idx}. {stop_info['name']['zh']}")

# 4. 測試獲取 ETA
print("\n" + "=" * 80)
print("4. 測試獲取 ETA")
print("=" * 80)
if routes:
    route_id = routes[0]
    try:
        etas = hketa.getEtas(route_id=route_id, seq=0, language="zh")
        print(f"路線 {route_id} 第一個站點的 ETA:")
        if etas:
            for idx, eta in enumerate(etas[:3]):
                print(f"  班次 {idx + 1}:")
                print(f"    預計到達: {eta.get('eta', '無數據')}")
                print(f"    備註: {eta.get('remark', '無')}")
        else:
            print("  目前無 ETA 數據")
    except Exception as e:
        print(f"  獲取 ETA 時發生錯誤: {e}")

# 5. 測試搜尋站點
print("\n" + "=" * 80)
print("5. 測試搜尋站點")
print("=" * 80)
search_keyword = "尖沙咀"
found_stops = []
for stop_id, stop_info in hketa.stop_list.items():
    name_zh = stop_info.get("name", {}).get("zh", "")
    if search_keyword in name_zh:
        found_stops.append({
            "id": stop_id,
            "name_zh": name_zh,
            "name_en": stop_info.get("name", {}).get("en", "")
        })
        if len(found_stops) >= 5:
            break

print(f"搜尋 '{search_keyword}' 的前 5 個結果:")
for stop in found_stops:
    print(f"  - {stop['name_zh']} ({stop['name_en']})")

# 6. 測試獲取假期列表
print("\n" + "=" * 80)
print("6. 測試獲取假期列表")
print("=" * 80)
holidays = hketa.holidays[:10]
print(f"前 10 個公眾假期:")
for holiday in holidays:
    year = holiday[:4]
    month = holiday[4:6]
    day = holiday[6:8]
    print(f"  - {year}年{month}月{day}日")

# 7. 測試站點映射
print("\n" + "=" * 80)
print("7. 測試站點映射")
print("=" * 80)
sample_stop_ids = list(hketa.stop_map.keys())[:3]
for stop_id in sample_stop_ids:
    mappings = hketa.stop_map.get(stop_id)
    if mappings:
        print(f"\n站點 {stop_id} 的映射:")
        for mapping in mappings:
            print(f"  - {mapping[0].upper()}: {mapping[1]}")

# 8. 統計資訊
print("\n" + "=" * 80)
print("8. 系統統計資訊")
print("=" * 80)
print(f"總路線數: {len(hketa.route_list)}")
print(f"總站點數: {len(hketa.stop_list)}")
print(f"站點映射數: {len(hketa.stop_map)}")
print(f"假期數量: {len(hketa.holidays)}")

# 統計各營運商路線數
operators = {}
for route_id, route_info in hketa.route_list.items():
    for co in route_info.get("co", []):
        operators[co] = operators.get(co, 0) + 1

print(f"\n各營運商路線數:")
for op, count in sorted(operators.items(), key=lambda x: x[1], reverse=True):
    print(f"  {op.upper()}: {count} 條路線")

print("\n" + "=" * 80)
print("✓ 所有測試完成!")
print("=" * 80)
