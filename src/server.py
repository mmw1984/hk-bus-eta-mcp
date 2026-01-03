#!/usr/bin/env python3
import os
import sys
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP
from hk_bus_eta import HKEta

# 初始化 FastMCP 伺服器
mcp = FastMCP("香港交通 ETA")

# 初始化 HKEta
# 注意：HKEta 可能需要一些時間來初始化，因為它會獲取路線數據
try:
    hketa = HKEta()
except Exception as e:
    print(f"初始化 HKEta 時出錯: {e}", file=sys.stderr)
    hketa = None

@mcp.tool(description="搜尋香港巴士或交通路線 ID，使用關鍵字（例如：'1'、'962X'、'TCL'）")
def search_routes(keyword: str) -> List[Dict[str, Any]]:
    """搜尋符合關鍵字的路線 ID，包含營運商資訊。"""
    if not hketa:
        return [{"error": "HKEta 未初始化"}]
    
    keyword = keyword.upper()
    routes = []
    
    for route_id, route_info in hketa.route_list.items():
        if keyword in route_id:
            routes.append({
                "route_id": route_id,
                "operators": route_info.get("co", []),
                "origin": route_info.get("orig", {}).get("zh", ""),
                "destination": route_info.get("dest", {}).get("zh", ""),
                "origin_en": route_info.get("orig", {}).get("en", ""),
                "destination_en": route_info.get("dest", {}).get("en", "")
            })
    
    return routes[:20]  # 限制為前 20 個結果

@mcp.tool(description="獲取香港交通路線特定站點的預計到達時間（ETA）")
def get_eta(route_id: str, seq: int = 0, language: str = "en") -> List[Dict[str, Any]]:
    """
    獲取指定路線的預計到達時間。
    
    參數：
        route_id: 路線的唯一識別碼（例如：'1+1+CHUK YUEN ESTATE+STAR FERRY'）
        seq: 站點序號（預設為 0，即第一個站點）
        language: 備註語言（'en' 或 'zh'）
    """
    if not hketa:
        return [{"error": "HKEta 未初始化"}]
    
    try:
        etas = hketa.getEtas(route_id=route_id, seq=seq, language=language)
        return etas
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool(description="獲取特定路線的詳細資料，包括其站點")
def get_route_details(route_id: str) -> Dict[str, Any]:
    """獲取路線的詳細資訊。"""
    if not hketa:
        return {"error": "HKEta 未初始化"}
    
    route_info = hketa.route_list.get(route_id)
    if not route_info:
        return {"error": "找不到路線"}
    
    return route_info

@mcp.tool(description="獲取路線的所有站點及其名稱和序號")
def get_route_stops(route_id: str, language: str = "en") -> List[Dict[str, Any]]:
    """
    獲取路線的詳細站點資訊，包括站點名稱。
    
    參數：
        route_id: 路線的唯一識別碼（例如：'1+1+CHUK YUEN ESTATE+STAR FERRY'）
        language: 站點名稱語言（'en' 或 'zh'，預設為 'en'）
    
    返回：
        包含站點序號、站點名稱和位置的列表
    """
    if not hketa:
        return [{"error": "HKEta 未初始化"}]
    
    route_info = hketa.route_list.get(route_id)
    if not route_info:
        return [{"error": "找不到路線"}]
    
    stops_result = []
    
    # 獲取此路線每個營運公司的站點
    for company, stop_ids in route_info.get("stops", {}).items():
        for idx, stop_id in enumerate(stop_ids):
            stop_info = hketa.stop_list.get(stop_id)
            if stop_info:
                stops_result.append({
                    "seq": idx,
                    "stop_id": stop_id,
                    "name": stop_info.get("name", {}).get(language, "未知"),
                    "name_en": stop_info.get("name", {}).get("en", ""),
                    "name_zh": stop_info.get("name", {}).get("zh", ""),
                    "location": stop_info.get("location", {}),
                    "company": company
                })
    
    return stops_result

@mcp.tool(description="獲取各營運商特定站點的 ETA（九巴 KMB）")
def get_kmb_eta(stop_id: str, route: str, service_type: str = "1", bound: str = "O") -> List[Dict[str, Any]]:
    """
    獲取九巴（KMB）特定站點的預計到達時間。
    
    參數：
        stop_id: 站點 ID
        route: 路線編號（例如：'1'）
        service_type: 服務類型（預設為 '1'）
        bound: 方向（'O' 為去程，'I' 為回程）
    """
    if not hketa:
        return [{"error": "HKEta 未初始化"}]
    
    try:
        seq = 0  # 序號可以從路線資訊中獲取
        etas = hketa.kmb(stop_id=stop_id, route=route, seq=seq, service_type=service_type, co="kmb", bound=bound)
        return etas
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool(description="獲取城巴/新巴（CTB）特定站點的 ETA")
def get_ctb_eta(stop_id: str, route: str, bound: str = "outbound", seq: int = 0) -> List[Dict[str, Any]]:
    """
    獲取城巴/新巴（CTB）特定站點的預計到達時間。
    
    參數：
        stop_id: 站點 ID
        route: 路線編號
        bound: 方向（'outbound' 或 'inbound'）
        seq: 站點序號
    """
    if not hketa:
        return [{"error": "HKEta 未初始化"}]
    
    try:
        etas = hketa.ctb(stop_id=stop_id, route=route, bound=bound, seq=seq)
        return etas
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool(description="獲取專線小巴（GMB）特定站點的 ETA")
def get_gmb_eta(gtfs_id: str, stop_id: str, bound: str = "1", seq: int = 0) -> List[Dict[str, Any]]:
    """
    獲取專線小巴（GMB）特定站點的預計到達時間。
    
    參數：
        gtfs_id: GTFS 路線 ID（例如：'HKI-20' 或 '37M'）
        stop_id: 站點 ID
        bound: 方向（'1' 或 '2'）
        seq: 站點序號
    
    注意：此方法可能不穩定，建議使用 get_eta() 通用方法配合完整的 route_id。
    例如：get_eta(route_id="20+1+San Po Kong+Tsz Wan Shan (North) (Circular)", seq=6, language="zh")
    """
    if not hketa:
        return [{"error": "HKEta 未初始化"}]
    
    try:
        # 記錄調試信息
        print(f"[GMB ETA] 查詢: gtfs_id={gtfs_id}, stop_id={stop_id}, bound={bound}, seq={seq}", file=sys.stderr)
        
        etas = hketa.gmb(gtfs_id=gtfs_id, stop_id=stop_id, bound=bound, seq=seq)
        
        # 如果結果為空，嘗試使用通用方法
        if not etas or len(etas) == 0:
            print(f"[GMB ETA] 空結果 - 嘗試使用通用方法", file=sys.stderr)
            
            # 嘗試搜索匹配的 GMB 路線
            route_number = gtfs_id.split('-')[-1] if '-' in gtfs_id else gtfs_id
            matching_gmb_routes = []
            
            for route_id, route_info in hketa.route_list.items():
                if route_number in route_id and 'gmb' in [co.lower() for co in route_info.get('co', [])]:
                    matching_gmb_routes.append({
                        "route_id": route_id,
                        "origin_zh": route_info.get("orig", {}).get("zh", ""),
                        "destination_zh": route_info.get("dest", {}).get("zh", "")
                    })
            
            return [{
                "info": "目前無可用的實時到站資料",
                "reason": "此綠專小巴路線可能沒有 GPS 追蹤或當前時段無服務",
                "suggestion": "建議使用 get_eta(route_id=..., seq=站點序號) 通用方法查詢",
                "matching_gmb_routes": matching_gmb_routes[:5],
                "example": "get_eta(route_id='20+1+San Po Kong+Tsz Wan Shan (North) (Circular)', seq=6, language='zh')"
            }]
        
        return etas
        
    except KeyError as e:
        # API 數據格式錯誤 - 嘗試使用通用方法
        print(f"[GMB ETA] KeyError: {e} - 嘗試搜索替代路線", file=sys.stderr)
        
        # 搜索匹配的 GMB 路線
        route_number = gtfs_id.split('-')[-1] if '-' in gtfs_id else gtfs_id
        matching_gmb_routes = []
        
        for route_id, route_info in hketa.route_list.items():
            if route_number in route_id and 'gmb' in [co.lower() for co in route_info.get('co', [])]:
                matching_gmb_routes.append({
                    "route_id": route_id,
                    "origin_zh": route_info.get("orig", {}).get("zh", ""),
                    "destination_zh": route_info.get("dest", {}).get("zh", "")
                })
        
        return [{
            "error": "直接 GMB API 查詢失敗",
            "suggestion": "請使用 get_eta() 通用方法配合下列路線 ID",
            "matching_gmb_routes": matching_gmb_routes[:5],
            "example": "get_eta(route_id='20+1+San Po Kong+Tsz Wan Shan (North) (Circular)', seq=6, language='zh')"
        }]
    except Exception as e:
        print(f"[GMB ETA] Exception: {type(e).__name__}: {e}", file=sys.stderr)
        return [{
            "error": str(e),
            "error_type": type(e).__name__,
            "suggestion": "請使用 search_routes_by_operator('gmb', '路線編號') 搜尋正確的路線 ID，然後使用 get_eta() 查詢"
        }]

@mcp.tool(description="獲取綠專小巴路線的站點序號信息（用於 get_eta 查詢）")
def get_gmb_route_stops(route_number: str) -> List[Dict[str, Any]]:
    """
    搜索綠專小巴路線並返回所有站點及其序號。
    
    參數：
        route_number: 路線編號（例如：'20', '37M'）
    
    返回：
        找到的 GMB 路線及其站點列表，包含用於 get_eta() 查詢的 seq 序號
    """
    if not hketa:
        return [{"error": "HKEta 未初始化"}]
    
    route_number_upper = route_number.upper()
    results = []
    
    for route_id, route_info in hketa.route_list.items():
        # 檢查是否為 GMB 路線且匹配路線編號
        operators = [co.lower() for co in route_info.get('co', [])]
        if 'gmb' not in operators:
            continue
        
        # 檢查路線編號匹配（路線 ID 格式: "20+1+San Po Kong+..."）
        route_parts = route_id.split('+')
        if len(route_parts) >= 1 and route_parts[0].upper() == route_number_upper:
            # 獲取此路線的站點
            stops_info = []
            for company, stop_ids in route_info.get("stops", {}).items():
                for seq, stop_id in enumerate(stop_ids):
                    stop_data = hketa.stop_list.get(stop_id, {})
                    stops_info.append({
                        "seq": seq,
                        "stop_id": stop_id,
                        "name_zh": stop_data.get("name", {}).get("zh", ""),
                        "name_en": stop_data.get("name", {}).get("en", ""),
                        "location": stop_data.get("location", {})
                    })
            
            results.append({
                "route_id": route_id,
                "origin_zh": route_info.get("orig", {}).get("zh", ""),
                "destination_zh": route_info.get("dest", {}).get("zh", ""),
                "origin_en": route_info.get("orig", {}).get("en", ""),
                "destination_en": route_info.get("dest", {}).get("en", ""),
                "stops": stops_info,
                "usage_example": f"get_eta(route_id='{route_id}', seq=站點序號, language='zh')"
            })
    
    if not results:
        return [{
            "error": f"找不到綠專小巴路線 {route_number}",
            "suggestion": "請使用 search_routes_by_operator('gmb') 查看所有 GMB 路線"
        }]
    
    return results

@mcp.tool(description="獲取港鐵（MTR）特定站點的 ETA")
def get_mtr_eta(stop_id: str, route: str, bound: str = "1") -> List[Dict[str, Any]]:
    """
    獲取港鐵（MTR）特定站點的預計到達時間。
    
    參數：
        stop_id: 站點 ID
        route: 路線編號
        bound: 方向
    """
    if not hketa:
        return [{"error": "HKEta 未初始化"}]
    
    try:
        etas = hketa.mtr(stop_id=stop_id, route=route, bound=bound)
        return etas
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool(description="獲取輕鐵（Light Rail）特定站點的 ETA")
def get_lightrail_eta(stop_id: str, route: str, dest_zh: str = "", dest_en: str = "") -> List[Dict[str, Any]]:
    """
    獲取輕鐵（Light Rail）特定站點的預計到達時間。
    
    參數：
        stop_id: 站點 ID（例如：'LR100'）
        route: 路線編號（例如：'505'）
        dest_zh: 目的地中文名稱（例如：'三聖'）
        dest_en: 目的地英文名稱（例如：'Sam Shing'）
    
    提示：建議使用 get_eta 並提供 route_id 來獲取輕鐵 ETA，更為簡單準確。
    """
    if not hketa:
        return [{"error": "HKEta 未初始化"}]
    
    try:
        # 構建 dest 字典，這是 hketa.lightrail 所需的格式
        dest = {"zh": dest_zh, "en": dest_en}
        etas = hketa.lightrail(stop_id=stop_id, route=route, dest=dest)
        return etas
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool(description="獲取輕鐵接駁巴士特定站點的 ETA")
def get_lrtfeeder_eta(stop_id: str, route: str, language: str = "en") -> List[Dict[str, Any]]:
    """
    獲取輕鐵接駁巴士特定站點的預計到達時間。
    
    參數：
        stop_id: 站點 ID（例如：'K65-U010'）
        route: 路線編號（例如：'K65'）
        language: 語言（'en' 或 'zh'）
    
    提示：建議使用 get_eta 並提供 route_id 來獲取輕鐵接駁巴士 ETA，更為簡單準確。
    """
    if not hketa:
        return [{"error": "HKEta 未初始化"}]
    
    try:
        etas = hketa.lrtfeeder(stop_id=stop_id, route=route, language=language)
        return etas
    except KeyError as e:
        return [{"error": f"找不到站點或路線資料: {str(e)}，請確認 stop_id 格式正確（例如：'K65-U010'）"}]
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool(description="獲取新大嶼山巴士（NLB）特定站點的 ETA")
def get_nlb_eta(stop_id: str, nlb_id: str) -> List[Dict[str, Any]]:
    """
    獲取新大嶼山巴士（NLB）特定站點的預計到達時間。
    
    參數：
        stop_id: 站點 ID
        nlb_id: NLB 路線 ID
    """
    if not hketa:
        return [{"error": "HKEta 未初始化"}]
    
    try:
        etas = hketa.nlb(stop_id=stop_id, nlb_id=nlb_id)
        return etas
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool(description="獲取所有路線列表")
def get_all_routes() -> Dict[str, Any]:
    """
    獲取所有可用的路線列表。
    
    返回：
        包含所有路線 ID 及其資訊的字典
    """
    if not hketa:
        return {"error": "HKEta 未初始化"}
    
    return {"total_routes": len(hketa.route_list), "sample_routes": list(hketa.route_list.keys())[:50]}

@mcp.tool(description="獲取所有站點列表")
def get_all_stops() -> Dict[str, Any]:
    """
    獲取所有可用的站點列表。
    
    返回：
        包含所有站點 ID 的資訊
    """
    if not hketa:
        return {"error": "HKEta 未初始化"}
    
    return {"total_stops": len(hketa.stop_list), "sample_stops": list(hketa.stop_list.keys())[:50]}

@mcp.tool(description="搜尋站點資訊")
def search_stops(keyword: str, language: str = "en") -> List[Dict[str, Any]]:
    """
    根據關鍵字搜尋站點。
    
    參數：
        keyword: 搜尋關鍵字
        language: 搜尋語言（'en' 或 'zh'）
    
    返回：
        符合條件的站點列表
    """
    if not hketa:
        return [{"error": "HKEta 未初始化"}]
    
    keyword_lower = keyword.lower()
    results = []
    
    for stop_id, stop_info in hketa.stop_list.items():
        name = stop_info.get("name", {}).get(language, "")
        if keyword_lower in name.lower():
            results.append({
                "stop_id": stop_id,
                "name_en": stop_info.get("name", {}).get("en", ""),
                "name_zh": stop_info.get("name", {}).get("zh", ""),
                "location": stop_info.get("location", {})
            })
            if len(results) >= 20:  # 限制結果數量
                break
    
    return results

@mcp.tool(description="搜尋特定營運商的路線（例如：綠專小巴 GMB）")
def search_routes_by_operator(operator: str = "gmb", keyword: str = "") -> List[Dict[str, Any]]:
    """
    根據營運商搜尋路線，可選擇性地過濾關鍵字。
    
    參數：
        operator: 營運商代碼（'gmb', 'kmb', 'ctb', 'nlb', 'mtr', 'lightrail', 'lrtfeeder'）
        keyword: 可選的路線編號關鍵字（例如：'37M', '20'）
    
    返回：
        符合條件的路線列表
    """
    if not hketa:
        return [{"error": "HKEta 未初始化"}]
    
    operator_lower = operator.lower()
    keyword_upper = keyword.upper() if keyword else ""
    results = []
    
    for route_id, route_info in hketa.route_list.items():
        operators = [co.lower() for co in route_info.get("co", [])]
        
        # 檢查營運商匹配
        if operator_lower in operators:
            # 如果有關鍵字，檢查是否匹配
            if not keyword_upper or keyword_upper in route_id:
                results.append({
                    "route_id": route_id,
                    "operators": route_info.get("co", []),
                    "origin_zh": route_info.get("orig", {}).get("zh", ""),
                    "destination_zh": route_info.get("dest", {}).get("zh", ""),
                    "origin_en": route_info.get("orig", {}).get("en", ""),
                    "destination_en": route_info.get("dest", {}).get("en", ""),
                    "service_type": route_info.get("service_type", "")
                })
                
                if len(results) >= 50:  # 限制結果數量
                    break
    
    return results

@mcp.tool(description="獲取香港公眾假期列表")
def get_holidays() -> List[str]:
    """
    獲取香港公眾假期列表。
    
    返回：
        假期日期列表（格式：YYYYMMDD）
    """
    if not hketa:
        return ["錯誤：HKEta 未初始化"]
    
    return hketa.holidays

@mcp.tool(description="獲取站點映射資訊")
def get_stop_mapping(stop_id: str) -> Dict[str, Any]:
    """
    獲取站點在不同營運商之間的映射關係。
    
    參數：
        stop_id: 站點 ID
    
    返回：
        站點在各營運商的對應資訊
    """
    if not hketa:
        return {"error": "HKEta 未初始化"}
    
    mapping = hketa.stop_map.get(stop_id)
    if not mapping:
        return {"error": "找不到站點映射"}
    
    return {"stop_id": stop_id, "mappings": mapping}

@mcp.tool(description="獲取站點詳細資訊")
def get_stop_info(stop_id: str) -> Dict[str, Any]:
    """
    獲取特定站點的詳細資訊。
    
    參數：
        stop_id: 站點 ID
    
    返回：
        站點的詳細資訊
    """
    if not hketa:
        return {"error": "HKEta 未初始化"}
    
    stop_info = hketa.stop_list.get(stop_id)
    if not stop_info:
        return {"error": "找不到站點"}
    
    return stop_info

@mcp.tool(description="獲取 MCP 伺服器資訊")
def get_server_info() -> dict:
    """獲取 MCP 伺服器的資訊。"""
    return {
        "server_name": "香港交通 ETA MCP 伺服器",
        "version": "2.0.0",
        "author": "Manus AI",
        "description": "提供香港公共交通即時到站時間，使用 data.gov.hk 和 hkbus.app 數據。",
        "python_version": sys.version.split()[0],
        "supported_operators": ["KMB", "CTB", "GMB", "MTR", "LightRail", "LRTFeeder", "NLB"],
        "total_routes": len(hketa.route_list) if hketa else 0,
        "total_stops": len(hketa.stop_list) if hketa else 0
    }

if __name__ == "__main__":
    # 使用 PORT 環境變數進行部署（例如在 Vercel 或 Render 上）
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"

    print(f"正在啟動香港交通 ETA MCP 伺服器於 {host}:{port}")

    mcp.run(
        transport="http",
        host=host,
        port=port,
        stateless_http=True
    )
