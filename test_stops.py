#!/usr/bin/env python3
"""測試獲取路線站點名稱的功能"""

from hk_bus_eta import HKEta
import json

print("正在初始化 HKEta...")
hketa = HKEta()

# 搜尋1號巴士路線
print("\n搜尋1號巴士路線...")
routes = [r for r in hketa.route_list.keys() if r.startswith("1+")]
print(f"找到 {len(routes)} 條路線")

# 選擇第一條路線
if routes:
    route_id = routes[0]
    print(f"\n獲取路線詳情: {route_id}")
    
    route_info = hketa.route_list.get(route_id)
    print(f"起點: {route_info['orig']['zh']} ({route_info['orig']['en']})")
    print(f"終點: {route_info['dest']['zh']} ({route_info['dest']['en']})")
    
    # 獲取站點資訊
    print(f"\n站點列表:")
    for company, stop_ids in route_info.get("stops", {}).items():
        print(f"\n營運商: {company.upper()}")
        print(f"{'序號':<4} {'中文站名':<40} {'英文站名':<50}")
        print("-" * 100)
        
        for idx, stop_id in enumerate(stop_ids[:10]):  # 只顯示前10個站點
            stop_info = hketa.stop_list.get(stop_id)
            if stop_info:
                name_zh = stop_info.get("name", {}).get("zh", "")
                name_en = stop_info.get("name", {}).get("en", "")
                print(f"{idx:<4} {name_zh:<40} {name_en:<50}")
        
        if len(stop_ids) > 10:
            print(f"... 還有 {len(stop_ids) - 10} 個站點")

print("\n測試完成!")
