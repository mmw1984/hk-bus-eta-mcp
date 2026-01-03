#!/usr/bin/env python3
"""
Vercel Serverless Function with Streaming Support for HK Transport MCP

This endpoint demonstrates streaming responses for real-time ETA updates.
"""
import sys
import os
import json
from typing import Iterator

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'src'))

from hk_bus_eta import HKEta

# Initialize HKEta
try:
    hketa = HKEta()
except Exception as e:
    print(f"Error initializing HKEta: {e}", file=sys.stderr)
    hketa = None


def stream_eta_updates(route_id: str, seq: int = 0, language: str = "en") -> Iterator[bytes]:
    """
    Stream ETA updates for a specific route and stop.
    
    Yields Server-Sent Events (SSE) format data.
    """
    if not hketa:
        yield b'data: {"error": "HKEta not initialized"}\n\n'
        return
    
    try:
        # Send initial status
        yield b'data: {"status": "connecting", "message": "Fetching ETA data..."}\n\n'
        
        # Get ETA data
        etas = hketa.getEtas(route_id=route_id, seq=seq, language=language)
        
        # Stream each ETA entry
        for idx, eta in enumerate(etas):
            data = json.dumps({
                "index": idx,
                "total": len(etas),
                "eta": eta
            })
            yield f'data: {data}\n\n'.encode('utf-8')
        
        # Send completion message
        yield b'data: {"status": "complete", "message": "All ETA data sent"}\n\n'
        
    except Exception as e:
        error_data = json.dumps({"error": str(e)})
        yield f'data: {error_data}\n\n'.encode('utf-8')


def stream_route_stops(route_id: str, language: str = "en") -> Iterator[bytes]:
    """
    Stream route stops information progressively.
    
    Yields Server-Sent Events (SSE) format data.
    """
    if not hketa:
        yield b'data: {"error": "HKEta not initialized"}\n\n'
        return
    
    try:
        route_info = hketa.route_list.get(route_id)
        if not route_info:
            yield b'data: {"error": "Route not found"}\n\n'
            return
        
        # Send initial status
        yield b'data: {"status": "connecting", "message": "Fetching route stops..."}\n\n'
        
        # Stream stops progressively
        for company, stop_ids in route_info.get("stops", {}).items():
            for idx, stop_id in enumerate(stop_ids):
                stop_info = hketa.stop_list.get(stop_id)
                if stop_info:
                    stop_data = {
                        "seq": idx,
                        "stop_id": stop_id,
                        "name": stop_info.get("name", {}).get(language, "Unknown"),
                        "name_en": stop_info.get("name", {}).get("en", ""),
                        "name_zh": stop_info.get("name", {}).get("zh", ""),
                        "location": stop_info.get("location", {}),
                        "company": company
                    }
                    data = json.dumps(stop_data)
                    yield f'data: {data}\n\n'.encode('utf-8')
        
        # Send completion message
        yield b'data: {"status": "complete", "message": "All stops sent"}\n\n'
        
    except Exception as e:
        error_data = json.dumps({"error": str(e)})
        yield f'data: {error_data}\n\n'.encode('utf-8')


def stream_search_results(keyword: str, search_type: str = "routes") -> Iterator[bytes]:
    """
    Stream search results progressively.
    
    Args:
        keyword: Search keyword
        search_type: 'routes' or 'stops'
    
    Yields Server-Sent Events (SSE) format data.
    """
    if not hketa:
        yield b'data: {"error": "HKEta not initialized"}\n\n'
        return
    
    try:
        yield b'data: {"status": "searching", "message": "Searching..."}\n\n'
        
        if search_type == "routes":
            keyword_upper = keyword.upper()
            routes = [r for r in hketa.route_list.keys() if keyword_upper in r]
            
            for idx, route in enumerate(routes[:50]):  # Limit to 50 results
                data = json.dumps({
                    "index": idx,
                    "route_id": route,
                    "info": hketa.route_list.get(route, {})
                })
                yield f'data: {data}\n\n'.encode('utf-8')
        
        elif search_type == "stops":
            keyword_lower = keyword.lower()
            count = 0
            
            for stop_id, stop_info in hketa.stop_list.items():
                name_en = stop_info.get("name", {}).get("en", "").lower()
                name_zh = stop_info.get("name", {}).get("zh", "").lower()
                
                if keyword_lower in name_en or keyword_lower in name_zh:
                    data = json.dumps({
                        "index": count,
                        "stop_id": stop_id,
                        "name_en": stop_info.get("name", {}).get("en", ""),
                        "name_zh": stop_info.get("name", {}).get("zh", ""),
                        "location": stop_info.get("location", {})
                    })
                    yield f'data: {data}\n\n'.encode('utf-8')
                    count += 1
                    
                    if count >= 50:  # Limit to 50 results
                        break
        
        yield b'data: {"status": "complete", "message": "Search complete"}\n\n'
        
    except Exception as e:
        error_data = json.dumps({"error": str(e)})
        yield f'data: {error_data}\n\n'.encode('utf-8')


class handler:
    """
    Vercel serverless function handler with streaming support.
    """
    
    def __init__(self, environ, start_response):
        self.environ = environ
        self.start_response = start_response
    
    def __iter__(self):
        """
        Enable streaming by making the handler iterable.
        """
        # Parse query parameters
        query_string = self.environ.get('QUERY_STRING', '')
        params = {}
        for param in query_string.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                params[key] = value
        
        # Get action type
        action = params.get('action', 'eta')
        
        # Set streaming headers
        self.start_response('200 OK', [
            ('Content-Type', 'text/event-stream'),
            ('Cache-Control', 'no-cache'),
            ('Connection', 'keep-alive'),
            ('X-Accel-Buffering', 'no'),  # Disable nginx buffering
        ])
        
        # Route to appropriate streaming function
        if action == 'eta':
            route_id = params.get('route_id', '')
            seq = int(params.get('seq', 0))
            language = params.get('language', 'en')
            
            if not route_id:
                yield b'data: {"error": "route_id parameter required"}\n\n'
                return
            
            yield from stream_eta_updates(route_id, seq, language)
        
        elif action == 'stops':
            route_id = params.get('route_id', '')
            language = params.get('language', 'en')
            
            if not route_id:
                yield b'data: {"error": "route_id parameter required"}\n\n'
                return
            
            yield from stream_route_stops(route_id, language)
        
        elif action == 'search':
            keyword = params.get('keyword', '')
            search_type = params.get('type', 'routes')
            
            if not keyword:
                yield b'data: {"error": "keyword parameter required"}\n\n'
                return
            
            yield from stream_search_results(keyword, search_type)
        
        else:
            error = json.dumps({
                "error": "Invalid action",
                "valid_actions": ["eta", "stops", "search"]
            })
            yield f'data: {error}\n\n'.encode('utf-8')


# WSGI-compatible entry point for Vercel
def application(environ, start_response):
    """
    WSGI application entry point.
    """
    return handler(environ, start_response)
