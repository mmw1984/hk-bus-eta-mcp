#!/usr/bin/env python3
import os
import sys
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastmcp import FastMCP
from hk_bus_eta import HKEta

load_dotenv()

mcp = FastMCP("香港交通 ETA")

try:
    hketa = HKEta()
except Exception as e:
    print(f"初始化 HKEta 時出錯: {e}", file=sys.stderr)
    hketa = None


def _err(message: str) -> Dict[str, str]:
    return {"error": message}


def _as_list_err(message: str) -> List[Dict[str, str]]:
    return [{"error": message}]


def _normalize_limit(limit: int, default_value: int, max_value: int) -> int:
    if limit <= 0:
        return default_value
    return min(limit, max_value)


def _route_number(route_id: str) -> str:
    parts = route_id.split("+")
    return parts[0] if parts else route_id


def _route_text(route_id: str, route_info: Dict[str, Any], language: str) -> str:
    orig = route_info.get("orig", {}).get(language, "")
    dest = route_info.get("dest", {}).get(language, "")
    return f"{route_id} {orig} {dest}".lower()


def _route_result(route_id: str, route_info: Dict[str, Any], language: str) -> Dict[str, Any]:
    return {
        "route_id": route_id,
        "route_number": _route_number(route_id),
        "operators": route_info.get("co", []),
        "origin": route_info.get("orig", {}).get(language, ""),
        "destination": route_info.get("dest", {}).get(language, ""),
        "origin_zh": route_info.get("orig", {}).get("zh", ""),
        "destination_zh": route_info.get("dest", {}).get("zh", ""),
        "origin_en": route_info.get("orig", {}).get("en", ""),
        "destination_en": route_info.get("dest", {}).get("en", ""),
        "service_type": route_info.get("service_type", ""),
    }


def _search_routes_core(keyword: str, operator: str, language: str, limit: int) -> List[Dict[str, Any]]:
    if not hketa:
        return _as_list_err("HKEta 未初始化")

    normalized_limit = _normalize_limit(limit, 50, 200)
    keyword_lower = keyword.strip().lower()
    operator_lower = operator.strip().lower()

    results: List[Dict[str, Any]] = []
    for route_id, route_info in hketa.route_list.items():
        operators = [co.lower() for co in route_info.get("co", [])]
        if operator_lower and operator_lower not in operators:
            continue

        if keyword_lower:
            text_zh = _route_text(route_id, route_info, "zh")
            text_en = _route_text(route_id, route_info, "en")
            if keyword_lower not in text_zh and keyword_lower not in text_en:
                continue

        results.append(_route_result(route_id, route_info, language))
        if len(results) >= normalized_limit:
            break

    return results


def _search_stops_core(keyword: str, language: str, limit: int) -> List[Dict[str, Any]]:
    if not hketa:
        return _as_list_err("HKEta 未初始化")

    normalized_limit = _normalize_limit(limit, 20, 200)
    keyword_lower = keyword.strip().lower()
    if not keyword_lower:
        return _as_list_err("keyword 不能為空")

    results: List[Dict[str, Any]] = []
    for stop_id, stop_info in hketa.stop_list.items():
        name_zh = stop_info.get("name", {}).get("zh", "")
        name_en = stop_info.get("name", {}).get("en", "")
        if keyword_lower in name_zh.lower() or keyword_lower in name_en.lower():
            results.append(
                {
                    "stop_id": stop_id,
                    "name": stop_info.get("name", {}).get(language, ""),
                    "name_zh": name_zh,
                    "name_en": name_en,
                    "location": stop_info.get("location", {}),
                }
            )
            if len(results) >= normalized_limit:
                break

    return results


def _route_stops_core(route_id: str, language: str, limit: int) -> Dict[str, Any]:
    if not hketa:
        return _err("HKEta 未初始化")

    route_info = hketa.route_list.get(route_id)
    if not route_info:
        return _err(f"找不到路線 ID: {route_id}")

    normalized_limit = _normalize_limit(limit, 9999, 9999)
    stops: List[Dict[str, Any]] = []

    for operator, stop_ids in route_info.get("stops", {}).items():
        if not isinstance(stop_ids, list):
            continue
        for seq, stop_id in enumerate(stop_ids):
            stop_info = hketa.stop_list.get(stop_id, {})
            stops.append(
                {
                    "seq": seq,
                    "operator": operator,
                    "stop_id": stop_id,
                    "name": stop_info.get("name", {}).get(language, ""),
                    "name_zh": stop_info.get("name", {}).get("zh", ""),
                    "name_en": stop_info.get("name", {}).get("en", ""),
                    "location": stop_info.get("location", {}),
                }
            )
            if len(stops) >= normalized_limit:
                break
        if len(stops) >= normalized_limit:
            break

    return {
        "route_id": route_id,
        "route_number": _route_number(route_id),
        "operators": route_info.get("co", []),
        "origin": route_info.get("orig", {}).get(language, ""),
        "destination": route_info.get("dest", {}).get(language, ""),
        "stops_count": len(stops),
        "stops": stops,
    }


def _get_eta_core(route_id: str, seq: int, language: str) -> List[Dict[str, Any]]:
    if not hketa:
        return _as_list_err("HKEta 未初始化")

    try:
        return hketa.getEtas(route_id=route_id, seq=seq, language=language)
    except Exception as e:
        return _as_list_err(str(e))


def _all_stops_eta_core(route_id: str, language: str, max_stops: int) -> Dict[str, Any]:
    if not hketa:
        return _err("HKEta 未初始化")

    route_info = hketa.route_list.get(route_id)
    if not route_info:
        return _err(f"找不到路線 ID: {route_id}")

    normalized_limit = _normalize_limit(max_stops, 20, 200)
    stops_eta: List[Dict[str, Any]] = []

    for operator, stop_ids in route_info.get("stops", {}).items():
        if not isinstance(stop_ids, list):
            continue
        for seq, stop_id in enumerate(stop_ids):
            stop_info = hketa.stop_list.get(stop_id, {})
            stop_name = stop_info.get("name", {}).get(language, "")
            try:
                etas = hketa.getEtas(route_id=route_id, seq=seq, language=language)
            except Exception as e:
                etas = [{"error": str(e)}]

            stops_eta.append(
                {
                    "seq": seq,
                    "operator": operator,
                    "stop_id": stop_id,
                    "stop_name": stop_name,
                    "etas": etas,
                }
            )
            if len(stops_eta) >= normalized_limit:
                break
        if len(stops_eta) >= normalized_limit:
            break

    return {
        "route_id": route_id,
        "route_number": _route_number(route_id),
        "operators": route_info.get("co", []),
        "origin": route_info.get("orig", {}).get(language, ""),
        "destination": route_info.get("dest", {}).get(language, ""),
        "max_stops": normalized_limit,
        "returned_stops": len(stops_eta),
        "stops_eta": stops_eta,
    }


@mcp.tool(description="中文：按關鍵字搜尋路線（可選營運商）")
def search_routes_zh(keyword: str = "", operator: str = "", limit: int = 50) -> List[Dict[str, Any]]:
    return _search_routes_core(keyword=keyword, operator=operator, language="zh", limit=limit)


@mcp.tool(description="English: search routes by keyword (optional operator filter)")
def search_routes_en(keyword: str = "", operator: str = "", limit: int = 50) -> List[Dict[str, Any]]:
    return _search_routes_core(keyword=keyword, operator=operator, language="en", limit=limit)


@mcp.tool(description="中文：按營運商搜尋路線")
def search_routes_by_operator_zh(operator: str = "gmb", keyword: str = "", limit: int = 50) -> List[Dict[str, Any]]:
    return _search_routes_core(keyword=keyword, operator=operator, language="zh", limit=limit)


@mcp.tool(description="English: search routes by operator")
def search_routes_by_operator_en(operator: str = "gmb", keyword: str = "", limit: int = 50) -> List[Dict[str, Any]]:
    return _search_routes_core(keyword=keyword, operator=operator, language="en", limit=limit)


@mcp.tool(description="中文：取得路線即時 ETA")
def get_eta_zh(route_id: str, seq: int = 0) -> List[Dict[str, Any]]:
    return _get_eta_core(route_id=route_id, seq=seq, language="zh")


@mcp.tool(description="English: get route ETA")
def get_eta_en(route_id: str, seq: int = 0) -> List[Dict[str, Any]]:
    return _get_eta_core(route_id=route_id, seq=seq, language="en")


@mcp.tool(description="中文：取得路線站點列表")
def get_route_stops_zh(route_id: str, limit: int = 9999) -> Dict[str, Any]:
    return _route_stops_core(route_id=route_id, language="zh", limit=limit)


@mcp.tool(description="English: get route stops")
def get_route_stops_en(route_id: str, limit: int = 9999) -> Dict[str, Any]:
    return _route_stops_core(route_id=route_id, language="en", limit=limit)


@mcp.tool(description="中文：批量取得路線多站 ETA（預設最多 20 站，較快）")
def get_route_all_stops_eta_zh(route_id: str, max_stops: int = 20) -> Dict[str, Any]:
    return _all_stops_eta_core(route_id=route_id, language="zh", max_stops=max_stops)


@mcp.tool(description="English: batch ETA for multiple stops on one route (default up to 20 stops)")
def get_route_all_stops_eta_en(route_id: str, max_stops: int = 20) -> Dict[str, Any]:
    return _all_stops_eta_core(route_id=route_id, language="en", max_stops=max_stops)


@mcp.tool(description="中文：搜尋站點")
def search_stops_zh(keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
    return _search_stops_core(keyword=keyword, language="zh", limit=limit)


@mcp.tool(description="English: search stops")
def search_stops_en(keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
    return _search_stops_core(keyword=keyword, language="en", limit=limit)


@mcp.tool(description="取得完整路線資料（原始 route_info）")
def get_route_details(route_id: str) -> Dict[str, Any]:
    if not hketa:
        return _err("HKEta 未初始化")
    route_info = hketa.route_list.get(route_id)
    if not route_info:
        return _err("找不到路線")
    return route_info


@mcp.tool(description="以路線編號找 route_id（例如 1、962X、K65）")
def find_route_ids_by_number(route_number: str, operator: str = "", limit: int = 20) -> List[Dict[str, Any]]:
    if not hketa:
        return _as_list_err("HKEta 未初始化")

    normalized_limit = _normalize_limit(limit, 20, 200)
    number_upper = route_number.strip().upper()
    operator_lower = operator.strip().lower()
    if not number_upper:
        return _as_list_err("route_number 不能為空")

    results: List[Dict[str, Any]] = []
    for route_id, route_info in hketa.route_list.items():
        if _route_number(route_id).upper() != number_upper:
            continue
        operators = [co.lower() for co in route_info.get("co", [])]
        if operator_lower and operator_lower not in operators:
            continue
        results.append(_route_result(route_id, route_info, "zh"))
        if len(results) >= normalized_limit:
            break

    return results


@mcp.tool(description="獲取各營運商特定站點的 ETA（九巴 KMB）")
def get_kmb_eta(stop_id: str, route: str, service_type: str = "1", bound: str = "O") -> List[Dict[str, Any]]:
    if not hketa:
        return _as_list_err("HKEta 未初始化")
    try:
        return hketa.kmb(stop_id=stop_id, route=route, seq=0, service_type=service_type, co="kmb", bound=bound)
    except Exception as e:
        return _as_list_err(str(e))


@mcp.tool(description="獲取城巴/新巴（CTB）特定站點的 ETA")
def get_ctb_eta(stop_id: str, route: str, bound: str = "outbound", seq: int = 0) -> List[Dict[str, Any]]:
    if not hketa:
        return _as_list_err("HKEta 未初始化")
    try:
        return hketa.ctb(stop_id=stop_id, route=route, bound=bound, seq=seq)
    except Exception as e:
        return _as_list_err(str(e))


@mcp.tool(description="獲取專線小巴（GMB）特定站點的 ETA")
def get_gmb_eta(gtfs_id: str, stop_id: str, bound: str = "1", seq: int = 0) -> List[Dict[str, Any]]:
    if not hketa:
        return _as_list_err("HKEta 未初始化")
    try:
        return hketa.gmb(gtfs_id=gtfs_id, stop_id=stop_id, bound=bound, seq=seq)
    except Exception as e:
        return _as_list_err(str(e))


@mcp.tool(description="獲取港鐵（MTR）特定站點的 ETA")
def get_mtr_eta(stop_id: str, route: str, bound: str = "1") -> List[Dict[str, Any]]:
    if not hketa:
        return _as_list_err("HKEta 未初始化")
    try:
        return hketa.mtr(stop_id=stop_id, route=route, bound=bound)
    except Exception as e:
        return _as_list_err(str(e))


@mcp.tool(description="獲取輕鐵（Light Rail）特定站點的 ETA")
def get_lightrail_eta(stop_id: str, route: str, dest_zh: str = "", dest_en: str = "") -> List[Dict[str, Any]]:
    if not hketa:
        return _as_list_err("HKEta 未初始化")
    try:
        return hketa.lightrail(stop_id=stop_id, route=route, dest={"zh": dest_zh, "en": dest_en})
    except Exception as e:
        return _as_list_err(str(e))


@mcp.tool(description="中文：獲取輕鐵接駁巴士 ETA")
def get_lrtfeeder_eta_zh(stop_id: str, route: str) -> List[Dict[str, Any]]:
    if not hketa:
        return _as_list_err("HKEta 未初始化")
    try:
        return hketa.lrtfeeder(stop_id=stop_id, route=route, language="zh")
    except Exception as e:
        return _as_list_err(str(e))


@mcp.tool(description="English: get LRT feeder ETA")
def get_lrtfeeder_eta_en(stop_id: str, route: str) -> List[Dict[str, Any]]:
    if not hketa:
        return _as_list_err("HKEta 未初始化")
    try:
        return hketa.lrtfeeder(stop_id=stop_id, route=route, language="en")
    except Exception as e:
        return _as_list_err(str(e))


@mcp.tool(description="獲取新大嶼山巴士（NLB）特定站點的 ETA")
def get_nlb_eta(stop_id: str, nlb_id: str) -> List[Dict[str, Any]]:
    if not hketa:
        return _as_list_err("HKEta 未初始化")
    try:
        return hketa.nlb(stop_id=stop_id, nlb_id=nlb_id)
    except Exception as e:
        return _as_list_err(str(e))


@mcp.tool(description="獲取所有路線數量與 sample")
def get_all_routes(limit: int = 50) -> Dict[str, Any]:
    if not hketa:
        return _err("HKEta 未初始化")
    normalized_limit = _normalize_limit(limit, 50, 500)
    return {
        "total_routes": len(hketa.route_list),
        "sample_routes": list(hketa.route_list.keys())[:normalized_limit],
    }


@mcp.tool(description="獲取所有站點數量與 sample")
def get_all_stops(limit: int = 50) -> Dict[str, Any]:
    if not hketa:
        return _err("HKEta 未初始化")
    normalized_limit = _normalize_limit(limit, 50, 500)
    return {
        "total_stops": len(hketa.stop_list),
        "sample_stops": list(hketa.stop_list.keys())[:normalized_limit],
    }


@mcp.tool(description="獲取香港公眾假期列表")
def get_holidays() -> List[str]:
    if not hketa:
        return ["錯誤：HKEta 未初始化"]
    return hketa.holidays


@mcp.tool(description="獲取站點映射資訊")
def get_stop_mapping(stop_id: str) -> Dict[str, Any]:
    if not hketa:
        return _err("HKEta 未初始化")
    mapping = hketa.stop_map.get(stop_id)
    if not mapping:
        return _err("找不到站點映射")
    return {"stop_id": stop_id, "mappings": mapping}


@mcp.tool(description="獲取站點詳細資訊")
def get_stop_info(stop_id: str) -> Dict[str, Any]:
    if not hketa:
        return _err("HKEta 未初始化")
    stop_info = hketa.stop_list.get(stop_id)
    if not stop_info:
        return _err("找不到站點")
    return stop_info


@mcp.tool(description="獲取 MCP 伺服器資訊")
def get_server_info() -> Dict[str, Any]:
    return {
        "server_name": "香港交通 ETA MCP 伺服器",
        "version": "3.0.0",
        "description": "語言分離（zh/en）工具設計，支援香港公共交通即時 ETA。",
        "python_version": sys.version.split()[0],
        "supported_operators": ["KMB", "CTB", "GMB", "MTR", "LightRail", "LRTFeeder", "NLB"],
        "total_routes": len(hketa.route_list) if hketa else 0,
        "total_stops": len(hketa.stop_list) if hketa else 0,
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"

    print(f"正在啟動香港交通 ETA MCP 伺服器於 {host}:{port}")

    mcp.run(
        transport="http",
        host=host,
        port=port,
        stateless_http=True,
    )
