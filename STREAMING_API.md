# Streaming API Documentation

## Overview

The HK Transport MCP now supports streaming responses using Server-Sent Events (SSE). Streaming allows real-time data delivery with progress updates, making it ideal for:

- Real-time ETA updates
- Batch processing with progress tracking
- Long-running queries
- Progressive data loading

## Endpoints

### 1. `/stream` - Single Route Streaming

Stream ETA and route information progressively.

#### Available Actions

##### Get ETA (Streaming)
```
GET /stream?action=eta&route_id=ROUTE_ID&seq=0&language=en
```

**Parameters:**
- `action`: Must be "eta"
- `route_id`: Route identifier (required)
- `seq`: Stop sequence number (default: 0)
- `language`: Language code - "en" or "zh" (default: "en")

**Example:**
```bash
curl -N "https://your-domain.vercel.app/stream?action=eta&route_id=1+1+CHUK+YUEN+ESTATE+STAR+FERRY&seq=0&language=en"
```

**Response Format (SSE):**
```
data: {"status": "connecting", "message": "Fetching ETA data..."}

data: {"index": 0, "total": 3, "eta": {...}}

data: {"index": 1, "total": 3, "eta": {...}}

data: {"status": "complete", "message": "All ETA data sent"}
```

##### Get Route Stops (Streaming)
```
GET /stream?action=stops&route_id=ROUTE_ID&language=en
```

**Parameters:**
- `action`: Must be "stops"
- `route_id`: Route identifier (required)
- `language`: Language code - "en" or "zh" (default: "en")

**Example:**
```bash
curl -N "https://your-domain.vercel.app/stream?action=stops&route_id=1+1+CHUK+YUEN+ESTATE+STAR+FERRY&language=en"
```

**Response Format (SSE):**
```
data: {"status": "connecting", "message": "Fetching route stops..."}

data: {"seq": 0, "stop_id": "...", "name": "...", "location": {...}}

data: {"seq": 1, "stop_id": "...", "name": "...", "location": {...}}

data: {"status": "complete", "message": "All stops sent"}
```

##### Search (Streaming)
```
GET /stream?action=search&keyword=KEYWORD&type=routes
```

**Parameters:**
- `action`: Must be "search"
- `keyword`: Search keyword (required)
- `type`: Search type - "routes" or "stops" (default: "routes")

**Example:**
```bash
curl -N "https://your-domain.vercel.app/stream?action=search&keyword=962&type=routes"
```

**Response Format (SSE):**
```
data: {"status": "searching", "message": "Searching..."}

data: {"index": 0, "route_id": "962X+...", "info": {...}}

data: {"index": 1, "route_id": "962B+...", "info": {...}}

data: {"status": "complete", "message": "Search complete"}
```

---

### 2. `/batch` - Batch Processing with Streaming

Process multiple routes or perform advanced queries with progress updates.

#### Available Modes

##### Batch ETA
```
GET /batch?mode=batch&route_ids=ROUTE1,ROUTE2,ROUTE3&language=en
```

**Parameters:**
- `mode`: Must be "batch"
- `route_ids`: Comma-separated list of route IDs (required)
- `language`: Language code - "en" or "zh" (default: "en")

**Example:**
```bash
curl -N "https://your-domain.vercel.app/batch?mode=batch&route_ids=1+1+CHUK+YUEN+ESTATE+STAR+FERRY,2+2+BAMBOO+GROVE+STAR+FERRY&language=en"
```

**Response Format (SSE):**
```
data: {"status": "started", "total": 2}

data: {"status": "processing", "current": 1, "total": 2, "route_id": "...", "progress_percent": 50}

data: {"status": "result", "route_id": "...", "index": 0, "etas": [...]}

data: {"status": "processing", "current": 2, "total": 2, "route_id": "...", "progress_percent": 100}

data: {"status": "result", "route_id": "...", "index": 1, "etas": [...]}

data: {"status": "complete", "total_processed": 2}
```

##### Nearby Stops
```
GET /batch?mode=nearby&lat=22.3193&lon=114.1694&radius=0.5
```

**Parameters:**
- `mode`: Must be "nearby"
- `lat`: Latitude (required)
- `lon`: Longitude (required)
- `radius`: Search radius in kilometers (default: 0.5)

**Example:**
```bash
curl -N "https://your-domain.vercel.app/batch?mode=nearby&lat=22.3193&lon=114.1694&radius=1.0"
```

**Response Format (SSE):**
```
data: {"status": "searching", "message": "Finding nearby stops..."}

data: {"status": "found", "count": 8}

data: {"status": "stop_info", "index": 0, "stop": {"stop_id": "...", "distance_km": 0.123, ...}}

data: {"status": "stop_info", "index": 1, "stop": {"stop_id": "...", "distance_km": 0.245, ...}}

data: {"status": "complete"}
```

##### Live Updates
```
GET /batch?mode=live&route_id=ROUTE_ID&duration=60&interval=30
```

**Parameters:**
- `mode`: Must be "live"
- `route_id`: Route identifier (required)
- `duration`: Total duration in seconds (default: 60)
- `interval`: Update interval in seconds (default: 30)

**Example:**
```bash
curl -N "https://your-domain.vercel.app/batch?mode=live&route_id=1+1+CHUK+YUEN+ESTATE+STAR+FERRY&duration=120&interval=30"
```

**Response Format (SSE):**
```
data: {"status": "started", "route_id": "...", "duration": 120}

data: {"status": "update", "update_number": 1, "elapsed_seconds": 0, "timestamp": 1234567890, "etas": [...]}

data: {"status": "update", "update_number": 2, "elapsed_seconds": 30, "timestamp": 1234567920, "etas": [...]}

data: {"status": "complete", "total_updates": 4}
```

---

## Usage Examples

### JavaScript/TypeScript (Browser)

```javascript
// Stream ETA updates
const eventSource = new EventSource('/stream?action=eta&route_id=1+1+CHUK+YUEN+ESTATE+STAR+FERRY');

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
  
  if (data.status === 'complete') {
    eventSource.close();
  }
};

eventSource.onerror = (error) => {
  console.error('Error:', error);
  eventSource.close();
};
```

### Python

```python
import requests

# Stream batch ETA
url = 'https://your-domain.vercel.app/batch'
params = {
    'mode': 'batch',
    'route_ids': 'ROUTE1,ROUTE2,ROUTE3',
    'language': 'en'
}

response = requests.get(url, params=params, stream=True)

for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            data = json.loads(line[6:])
            print(data)
```

### cURL

```bash
# Stream nearby stops
curl -N "https://your-domain.vercel.app/batch?mode=nearby&lat=22.3193&lon=114.1694&radius=0.5"
```

---

## Benefits of Streaming

1. **Real-time Updates**: Get data as soon as it's available
2. **Progress Tracking**: Monitor long-running operations
3. **Reduced Memory**: Process large datasets without loading everything into memory
4. **Better UX**: Show progress to users instead of waiting for complete response
5. **Extended Runtime**: Vercel streaming functions support longer execution times with extended runtime logs

---

## Error Handling

All streaming endpoints return errors in the same SSE format:

```
data: {"error": "Error description"}
```

Or for recoverable errors within a stream:

```
data: {"status": "error", "error": "Error description", "route_id": "..."}
```

---

## Configuration

The streaming endpoints are configured in `vercel.json` with:
- `maxDuration: 300` (5 minutes for streaming operations)
- `memory: 1024` MB
- Appropriate headers for SSE (Server-Sent Events)

---

## Notes

- Streaming responses use the Server-Sent Events (SSE) protocol
- Use the `-N` flag with cURL to disable buffering
- In JavaScript, use `EventSource` API for automatic reconnection
- For Python, use `stream=True` with requests library
- All streaming endpoints support CORS for browser usage
- Extended runtime logs will show real-time output during streaming
