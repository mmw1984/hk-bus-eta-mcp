from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "ok",
            "message": "HK Bus ETA MCP Server is running",
            "version": "2.0.0",
            "endpoints": {
                "mcp": {
                    "path": "/mcp",
                    "description": "MCP server endpoint for Claude Desktop integration",
                    "type": "ASGI application"
                },
                "stream": {
                    "path": "/stream",
                    "description": "Server-Sent Events streaming endpoint",
                    "type": "Streaming",
                    "actions": ["eta", "stops", "search"],
                    "example": "/stream?action=eta&route_id=ROUTE_ID&language=en"
                },
                "batch": {
                    "path": "/batch",
                    "description": "Batch processing with streaming progress updates",
                    "type": "Streaming",
                    "modes": ["batch", "nearby", "live"],
                    "examples": {
                        "batch": "/batch?mode=batch&route_ids=ROUTE1,ROUTE2",
                        "nearby": "/batch?mode=nearby&lat=22.3193&lon=114.1694",
                        "live": "/batch?mode=live&route_id=ROUTE_ID&duration=60"
                    }
                }
            },
            "features": [
                "Real-time ETA for Hong Kong public transport",
                "Support for KMB, CTB, GMB, MTR, Light Rail, LRT Feeder, NLB",
                "Server-Sent Events (SSE) streaming",
                "Batch processing with progress tracking",
                "Geospatial queries for nearby stops",
                "Live ETA updates"
            ],
            "documentation": {
                "streaming_api": "See STREAMING_API.md for detailed API documentation",
                "streaming_guide": "See STREAMING_GUIDE.md for implementation guide",
                "demo": "Open streaming_demo.html for interactive demo"
            }
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode())
        return
