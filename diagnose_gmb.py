#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
診斷綠色專線小巴 (GMB) ETA 問題

這個腳本會測試不同的綠專小巴查詢方法，並提供詳細的調試信息。
"""

import sys
import json
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from hk_bus_eta import HKEta

def print_section(title):
    """打印分隔線"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def diagnose_gmb_routes():
    """診斷綠專小巴路線"""
    print_section("初始化 HKEta")
    
    try:
        hketa = HKEta()
        print("✓ HKEta 初始化成功")
    except Exception as e:
        print(f"✗ HKEta 初始化失敗: {e}")
        return
    
    # 測試路線: 37M 和 20
    test_cases = [
        {
            "name": "37M - 聖文德書院",
            "route": "37M",
            "stop_id": "20000820",
            "region": "NT"  # New Territories
        },
        {
            "name": "20 - 聖母醫院",
            "route": "20",
            "stop_id": "20012706",
            "region": "HK"  # Hong Kong Island
        },
        {
            "name": "20 - San Po Kong (JavaScript 成功案例)",
            "route": "20",
            "route_id": "20+1+San Po Kong+Tsz Wan Shan (North) (Circular)",
            "stop_id": "20012706",
            "seq": 6,
            "region": "HK"
        }
    ]
    
    print_section("檢查路線列表")
    
    # 搜索所有綠專小巴路線
    gmb_routes = {}
    for route_id, route_info in hketa.route_list.items():
        # 綠專小巴路線 ID 通常包含特定格式
        if any(keyword in route_id for keyword in ["GMB", "20+", "37M+"]):
            gmb_routes[route_id] = route_info
            print(f"找到路線: {route_id}")
    
    print(f"\n總共找到 {len(gmb_routes)} 條綠專小巴相關路線")
    
    print_section("搜索特定路線")
    
    for test_case in test_cases:
        route = test_case["route"]
        print(f"\n搜索路線: {route}")
        
        # 搜索包含路線編號的所有路線
        matching_routes = [r for r in hketa.route_list.keys() if route in r]
        
        if matching_routes:
            print(f"  找到 {len(matching_routes)} 個匹配的路線:")
            for r in matching_routes[:10]:  # 限制顯示前10個
                route_info = hketa.route_list[r]
                print(f"    - {r}")
                print(f"      營運商: {route_info.get('co', 'N/A')}")
                print(f"      起點: {route_info.get('orig', {}).get('zh', 'N/A')}")
                print(f"      終點: {route_info.get('dest', {}).get('zh', 'N/A')}")
        else:
            print(f"  ✗ 沒有找到路線 {route}")
    
    print_section("檢查站點信息")
    
    for test_case in test_cases:
        stop_id = test_case["stop_id"]
        name = test_case["name"]
        
        print(f"\n站點: {name} (ID: {stop_id})")
        
        if stop_id in hketa.stop_list:
            stop_info = hketa.stop_list[stop_id]
            print(f"  ✓ 站點存在")
            print(f"  名稱 (中): {stop_info.get('name', {}).get('zh', 'N/A')}")
            print(f"  名稱 (英): {stop_info.get('name', {}).get('en', 'N/A')}")
            print(f"  位置: {stop_info.get('location', {})}")
        else:
            print(f"  ✗ 站點不存在於 stop_list 中")
    
    print_section("測試 GMB ETA 查詢")
    
    # 嘗試構建正確的 GTFS ID
    for test_case in test_cases:
        route = test_case["route"]
        stop_id = test_case["stop_id"]
        name = test_case["name"]
        region = test_case["region"]
        
        print(f"\n測試: {name}")
        
        # 嘗試不同的 GTFS ID 格式
        gtfs_formats = [
            f"{route}",
            f"GMB-{route}",
            f"{region}-{route}",
            f"HKI-{route}" if region == "HK" else f"NT-{route}",
        ]
        
        # 也嘗試搜索匹配的路線
        matching_routes = [r for r in hketa.route_list.keys() if route in r and "GMB" in r.upper()]
        if matching_routes:
            print(f"  找到 {len(matching_routes)} 個可能的 GMB 路線:")
            for mr in matching_routes[:5]:
                gtfs_formats.append(mr)
                print(f"    - {mr}")
        
        for gtfs_id in gtfs_formats:
            try:
                print(f"\n  嘗試 GTFS ID: {gtfs_id}")
                
                # 嘗試不同的 bound 值
                for bound in ["1", "2", "O", "I"]:
                    try:
                        etas = hketa.gmb(gtfs_id=gtfs_id, stop_id=stop_id, bound=bound, seq=0)
                        
                        if etas and len(etas) > 0:
                            print(f"    ✓ 成功 (bound={bound})! 獲得 {len(etas)} 個 ETA:")
                            for eta in etas[:3]:  # 顯示前3個
                                print(f"      {json.dumps(eta, ensure_ascii=False, indent=8)}")
                            break
                        else:
                            print(f"    - bound={bound}: 空結果")
                    except Exception as e:
                        print(f"    ✗ bound={bound}: {type(e).__name__}: {str(e)[:100]}")
                        
            except Exception as e:
                print(f"  ✗ 錯誤: {type(e).__name__}: {str(e)[:100]}")
    
    print_section("使用 getEtas 通用方法測試")
    
    # 嘗試使用通用的 getEtas 方法
    for test_case in test_cases:
        route = test_case["route"]
        name = test_case["name"]
        
        print(f"\n測試: {name}")
        
        # 如果有特定的 route_id，優先測試
        if "route_id" in test_case:
            route_id = test_case["route_id"]
            seq = test_case.get("seq", 0)
            
            print(f"  測試特定路線: {route_id} (seq={seq})")
            try:
                etas = hketa.getEtas(route_id=route_id, seq=seq, language="zh")
                
                if etas and len(etas) > 0:
                    print(f"    ✓✓✓ 成功! 獲得 {len(etas)} 個 ETA")
                    for idx, eta in enumerate(etas):
                        print(f"    ETA {idx+1}: {json.dumps(eta, ensure_ascii=False, indent=6)}")
                else:
                    print(f"    - 空結果")
            except Exception as e:
                print(f"    ✗ 錯誤: {type(e).__name__}: {str(e)}")
                import traceback
                traceback.print_exc()
            continue
        
        # 搜索包含路線的所有 route_id
        matching_routes = [r for r in hketa.route_list.keys() if route in r]
        
        if matching_routes:
            print(f"  找到 {len(matching_routes)} 個匹配路線，測試前3個:")
            for route_id in matching_routes[:3]:
                try:
                    print(f"\n  路線 ID: {route_id}")
                    etas = hketa.getEtas(route_id=route_id, seq=0, language="zh")
                    
                    if etas and len(etas) > 0:
                        print(f"    ✓ 成功! 獲得 {len(etas)} 個 ETA")
                        print(f"    第一個 ETA: {json.dumps(etas[0], ensure_ascii=False, indent=6)}")
                    else:
                        print(f"    - 空結果")
                        
                except Exception as e:
                    print(f"    ✗ 錯誤: {type(e).__name__}: {str(e)[:100]}")
    
    print_section("檢查 HKEta 方法簽名")
    
    # 檢查 gmb 方法的實際簽名
    import inspect
    
    if hasattr(hketa, 'gmb'):
        print("\nhketa.gmb 方法簽名:")
        sig = inspect.signature(hketa.gmb)
        print(f"  {sig}")
        
        # 獲取文檔字符串
        if hketa.gmb.__doc__:
            print("\n文檔:")
            print(f"  {hketa.gmb.__doc__}")
    
    print_section("診斷完成")
    print("\n建議:")
    print("1. 檢查上述輸出中是否找到了正確的路線 ID")
    print("2. 確認 GTFS ID 的正確格式")
    print("3. 如果所有方法都返回空結果，可能是:")
    print("   - 這些路線沒有實時 GPS 追蹤")
    print("   - 當前時間沒有服務")
    print("   - API 數據源暫時不可用")
    print("4. 考慮添加更詳細的錯誤處理和日誌")
    print()

if __name__ == "__main__":
    try:
        diagnose_gmb_routes()
    except Exception as e:
        print(f"\n致命錯誤: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
