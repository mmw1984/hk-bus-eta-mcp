#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""測試新的路線查詢和 ETA 工具"""

import sys
import io
import json

# 設置 UTF-8 輸出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'c:/Users/mmw1984/Downloads/hk-transport-mcp-updated')

from hk_bus_eta import HKEta

def test_search_routes():
    """測試 search_routes 功能"""
    print("\n=== 測試 1: 搜尋路線 '1' ===")
    hketa = HKEta()
    
    keyword = "1"
    keyword_upper = keyword.upper()
    routes = []
    
    for route_id, route_info in hketa.route_list.items():
        if keyword_upper in route_id:
            parts = route_id.split('+')
            route_number = parts[0] if len(parts) > 0 else route_id
            
            routes.append({
                "route_id": route_id,
                "route_number": route_number,
                "operators": route_info.get("co", []),
                "origin_zh": route_info.get("orig", {}).get("zh", ""),
                "destination_zh": route_info.get("dest", {}).get("zh", ""),
                "description": f"{route_number} ({', '.join(route_info.get('co', []))}) {route_info.get('orig', {}).get('zh', '')} → {route_info.get('dest', {}).get('zh', '')}"
            })
    
    # 只顯示前 5 個
    for route in routes[:5]:
        print(f"  {route['description']}")
    print(f"\n共找到 {len(routes)} 條路線\n")

def test_get_route_stops():
    """測試 get_route_stops 功能"""
    print("\n=== 測試 2: 獲取路線站點 ===")
    hketa = HKEta()
    
    route_id = "20+1+San Po Kong+Tsz Wan Shan (North) (Circular)"
    route_info = hketa.route_list.get(route_id)
    
    if not route_info:
        print(f"找不到路線: {route_id}")
        return
    
    stops_data = route_info.get("stops", {})
    stops_list = []
    
    # stops 結構是 {"營運商": [stop_id1, stop_id2, ...]}
    for operator, stop_ids in stops_data.items():
        if isinstance(stop_ids, list):
            for seq, stop_id in enumerate(stop_ids):
                stop_info = hketa.stop_list.get(stop_id, {})
                
                stops_list.append({
                    "seq": seq,
                    "stop_id": stop_id,
                    "name_zh": stop_info.get("name", {}).get("zh", ""),
                    "operator": operator
                })
    
    stops_list.sort(key=lambda x: x["seq"])
    
    print(f"路線: {route_id}")
    print(f"站點數: {len(stops_list)}")
    print("\n前 5 個站點:")
    for stop in stops_list[:5]:
        print(f"  [{stop['seq']}] {stop['name_zh']} (ID: {stop['stop_id']})")

def test_get_route_all_stops_eta():
    """測試 get_route_all_stops_eta 功能（只測試前 3 個站點）"""
    print("\n=== 測試 3: 獲取路線所有站點 ETA (前 3 站) ===")
    hketa = HKEta()
    
    route_id = "20+1+San Po Kong+Tsz Wan Shan (North) (Circular)"
    route_info = hketa.route_list.get(route_id)
    
    if not route_info:
        print(f"找不到路線: {route_id}")
        return
    
    stops_data = route_info.get("stops", {})
    all_stops_eta = []
    
    # 只測試前 3 個站點
    for operator, stop_ids in stops_data.items():
        if isinstance(stop_ids, list):
            for seq, stop_id in enumerate(stop_ids[:3]):  # 只取前 3 個
                stop_info = hketa.stop_list.get(stop_id, {})
                stop_name = stop_info.get("name", {}).get("zh", "")
                
                print(f"\n站點 [{seq}] {stop_name}")
                
                try:
                    eta_data = hketa.getEtas(route_id=route_id, seq=seq, language="zh")
                    
                    etas = []
                    if isinstance(eta_data, list):
                        for eta in eta_data:
                            time_str = eta.get("eta", eta.get("time", ""))
                            remark = eta.get("rmk", {}).get("zh", eta.get("remark", ""))
                            print(f"  → {time_str} {remark}")
                            etas.append({
                                "time": time_str,
                                "remark": remark,
                            })
                    
                    all_stops_eta.append({
                        "seq": seq,
                        "stop_name": stop_name,
                        "etas": etas,
                        "has_eta": len(etas) > 0
                    })
                except Exception as e:
                    print(f"  錯誤: {e}")
                    all_stops_eta.append({
                        "seq": seq,
                        "stop_name": stop_name,
                        "etas": [],
                        "has_eta": False,
                        "error": str(e)
                    })
    
    stops_with_eta = sum(1 for stop in all_stops_eta if stop["has_eta"])
    print(f"\n總共 {len(all_stops_eta)} 個站點，{stops_with_eta} 個有 ETA 數據")

if __name__ == "__main__":
    print("開始測試新工具...")
    test_search_routes()
    test_get_route_stops()
    test_get_route_all_stops_eta()
    print("\n測試完成！")
