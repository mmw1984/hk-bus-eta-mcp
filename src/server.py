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
def search_routes(keyword: str) -> List[str]:
    """搜尋符合關鍵字的路線 ID。"""
    if not hketa:
        return ["錯誤：HKEta 未初始化"]
    
    keyword = keyword.upper()
    routes = [r for r in hketa.route_list.keys() if keyword in r]
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
        gtfs_id: GTFS 路線 ID
        stop_id: 站點 ID
        bound: 方向
        seq: 站點序號
    """
    if not hketa:
        return [{"error": "HKEta 未初始化"}]
    
    try:
        etas = hketa.gmb(gtfs_id=gtfs_id, stop_id=stop_id, bound=bound, seq=seq)
        return etas
    except Exception as e:
        return [{"error": str(e)}]

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
