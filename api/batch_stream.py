#!/usr/bin/env python3
"""
Vercel Serverless Function - Batch ETA Streaming

This endpoint demonstrates batch processing with streaming progress updates.
Useful for fetching ETA for multiple stops/routes simultaneously.
"""
import sys
import os
import json
import time
from typing import Iterator, List, Dict, Any

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


def stream_batch_eta(route_ids: List[str], language: str = "en") -> Iterator[bytes]:
    """
    Stream ETA updates for multiple routes with progress tracking.
    
    Args:
        route_ids: List of route IDs to fetch
        language: Language for ETA data
    
    Yields Server-Sent Events (SSE) format data.
    """
    if not hketa:
        yield b'data: {"error": "HKEta not initialized"}\n\n'
        return
    
    try:
        total = len(route_ids)
        yield f'data: {json.dumps({"status": "started", "total": total})}\n\n'.encode('utf-8')
        
        for idx, route_id in enumerate(route_ids):
            try:
                # Send progress update
                progress = {
                    "status": "processing",
                    "current": idx + 1,
                    "total": total,
                    "route_id": route_id,
                    "progress_percent": int((idx + 1) / total * 100)
                }
                yield f'data: {json.dumps(progress)}\n\n'.encode('utf-8')
                
                # Fetch ETA
                etas = hketa.getEtas(route_id=route_id, seq=0, language=language)
                
                # Send result
                result = {
                    "status": "result",
                    "route_id": route_id,
                    "index": idx,
                    "etas": etas
                }
                yield f'data: {json.dumps(result)}\n\n'.encode('utf-8')
                
            except Exception as e:
                # Send error for this specific route
                error = {
                    "status": "error",
                    "route_id": route_id,
                    "index": idx,
                    "error": str(e)
                }
                yield f'data: {json.dumps(error)}\n\n'.encode('utf-8')
        
        # Send completion
        yield f'data: {json.dumps({"status": "complete", "total_processed": total})}\n\n'.encode('utf-8')
        
    except Exception as e:
        error_data = json.dumps({"status": "fatal_error", "error": str(e)})
        yield f'data: {error_data}\n\n'.encode('utf-8')


def stream_nearby_stops_eta(lat: float, lon: float, radius_km: float = 0.5) -> Iterator[bytes]:
    """
    Stream ETA for stops near a given location.
    
    Args:
        lat: Latitude
        lon: Longitude
        radius_km: Search radius in kilometers
    
    Yields Server-Sent Events (SSE) format data.
    """
    if not hketa:
        yield b'data: {"error": "HKEta not initialized"}\n\n'
        return
    
    try:
        yield b'data: {"status": "searching", "message": "Finding nearby stops..."}\n\n'
        
        # Simple distance calculation (rough approximation)
        def distance(lat1, lon1, lat2, lon2):
            """Calculate rough distance in km using Pythagorean approximation."""
            lat_diff = (lat2 - lat1) * 111.0  # 1 degree latitude ≈ 111 km
            lon_diff = (lon2 - lon1) * 111.0 * 0.8  # Adjust for Hong Kong latitude
            return (lat_diff**2 + lon_diff**2)**0.5
        
        nearby_stops = []
        
        # Find nearby stops
        for stop_id, stop_info in hketa.stop_list.items():
            location = stop_info.get("location", {})
            stop_lat = location.get("lat")
            stop_lon = location.get("lng")
            
            if stop_lat and stop_lon:
                dist = distance(lat, lon, stop_lat, stop_lon)
                if dist <= radius_km:
                    nearby_stops.append({
                        "stop_id": stop_id,
                        "distance_km": round(dist, 3),
                        "name_en": stop_info.get("name", {}).get("en", ""),
                        "name_zh": stop_info.get("name", {}).get("zh", ""),
                        "location": location
                    })
        
        # Sort by distance
        nearby_stops.sort(key=lambda x: x["distance_km"])
        
        # Limit to 10 nearest stops
        nearby_stops = nearby_stops[:10]
        
        yield f'data: {json.dumps({"status": "found", "count": len(nearby_stops)})}\n\n'.encode('utf-8')
        
        # Stream stop information
        for idx, stop in enumerate(nearby_stops):
            data = {
                "status": "stop_info",
                "index": idx,
                "stop": stop
            }
            yield f'data: {json.dumps(data)}\n\n'.encode('utf-8')
        
        yield b'data: {"status": "complete"}\n\n'
        
    except Exception as e:
        error_data = json.dumps({"error": str(e)})
        yield f'data: {error_data}\n\n'.encode('utf-8')


def stream_live_updates(route_id: str, duration_seconds: int = 60, interval_seconds: int = 30) -> Iterator[bytes]:
    """
    Stream live ETA updates at regular intervals.
    
    Args:
        route_id: Route ID to monitor
        duration_seconds: Total duration to stream
        interval_seconds: Update interval
    
    Yields Server-Sent Events (SSE) format data.
    """
    if not hketa:
        yield b'data: {"error": "HKEta not initialized"}\n\n'
        return
    
    try:
        start_time = time.time()
        update_count = 0
        
        yield f'data: {json.dumps({"status": "started", "route_id": route_id, "duration": duration_seconds})}\n\n'.encode('utf-8')
        
        while (time.time() - start_time) < duration_seconds:
            try:
                # Fetch current ETA
                etas = hketa.getEtas(route_id=route_id, seq=0, language="en")
                
                update_count += 1
                elapsed = int(time.time() - start_time)
                
                data = {
                    "status": "update",
                    "update_number": update_count,
                    "elapsed_seconds": elapsed,
                    "timestamp": time.time(),
                    "etas": etas
                }
                yield f'data: {json.dumps(data)}\n\n'.encode('utf-8')
                
                # Wait for next interval
                time.sleep(interval_seconds)
                
            except Exception as e:
                error = {
                    "status": "error",
                    "update_number": update_count,
                    "error": str(e)
                }
                yield f'data: {json.dumps(error)}\n\n'.encode('utf-8')
        
        yield f'data: {json.dumps({"status": "complete", "total_updates": update_count})}\n\n'.encode('utf-8')
        
    except Exception as e:
        error_data = json.dumps({"status": "fatal_error", "error": str(e)})
        yield f'data: {error_data}\n\n'.encode('utf-8')


class handler:
    """
    Vercel serverless function handler for batch streaming operations.
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
        
        # Get mode
        mode = params.get('mode', 'batch')
        
        # Set streaming headers
        self.start_response('200 OK', [
            ('Content-Type', 'text/event-stream'),
            ('Cache-Control', 'no-cache'),
            ('Connection', 'keep-alive'),
            ('X-Accel-Buffering', 'no'),
        ])
        
        # Route to appropriate streaming function
        if mode == 'batch':
            # Expect route_ids as comma-separated list
            route_ids_str = params.get('route_ids', '')
            language = params.get('language', 'en')
            
            if not route_ids_str:
                yield b'data: {"error": "route_ids parameter required (comma-separated)"}\n\n'
                return
            
            route_ids = [r.strip() for r in route_ids_str.split(',') if r.strip()]
            yield from stream_batch_eta(route_ids, language)
        
        elif mode == 'nearby':
            try:
                lat = float(params.get('lat', 0))
                lon = float(params.get('lon', 0))
                radius = float(params.get('radius', 0.5))
                
                if lat == 0 or lon == 0:
                    yield b'data: {"error": "lat and lon parameters required"}\n\n'
                    return
                
                yield from stream_nearby_stops_eta(lat, lon, radius)
                
            except ValueError:
                yield b'data: {"error": "Invalid lat/lon/radius values"}\n\n'
        
        elif mode == 'live':
            route_id = params.get('route_id', '')
            duration = int(params.get('duration', 60))
            interval = int(params.get('interval', 30))
            
            if not route_id:
                yield b'data: {"error": "route_id parameter required"}\n\n'
                return
            
            yield from stream_live_updates(route_id, duration, interval)
        
        else:
            error = json.dumps({
                "error": "Invalid mode",
                "valid_modes": ["batch", "nearby", "live"]
            })
            yield f'data: {error}\n\n'.encode('utf-8')


# WSGI-compatible entry point for Vercel
def application(environ, start_response):
    """
    WSGI application entry point.
    """
    return handler(environ, start_response)
