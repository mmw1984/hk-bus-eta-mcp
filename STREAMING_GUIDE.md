# Streaming Python Functions - Quick Reference

## Overview

This project demonstrates how to implement streaming responses in Vercel Python Functions using Server-Sent Events (SSE).

## Key Concepts

### 1. Streaming Handler Pattern

Vercel Python runtime supports streaming through iterable handlers:

```python
class handler:
    def __init__(self, environ, start_response):
        self.environ = environ
        self.start_response = start_response
    
    def __iter__(self):
        """Make handler iterable for streaming."""
        # Set streaming headers
        self.start_response('200 OK', [
            ('Content-Type', 'text/event-stream'),
            ('Cache-Control', 'no-cache'),
            ('Connection', 'keep-alive'),
            ('X-Accel-Buffering', 'no'),
        ])
        
        # Yield data progressively
        yield b'data: {"status": "started"}\n\n'
        yield b'data: {"status": "processing"}\n\n'
        yield b'data: {"status": "complete"}\n\n'
```

### 2. Server-Sent Events Format

SSE format requires:
- Each message prefixed with `data: `
- Each message terminated with `\n\n`
- Data should be JSON-encoded

```python
def stream_data():
    data = {"message": "Hello"}
    yield f'data: {json.dumps(data)}\n\n'.encode('utf-8')
```

### 3. Generator Functions

Use Python generators to stream data:

```python
def stream_items(items: List[Any]) -> Iterator[bytes]:
    """Stream items progressively."""
    for idx, item in enumerate(items):
        data = {
            "index": idx,
            "item": item,
            "progress": (idx + 1) / len(items) * 100
        }
        yield f'data: {json.dumps(data)}\n\n'.encode('utf-8')
    
    yield b'data: {"status": "complete"}\n\n'
```

## Implementation Files

### 1. `/api/stream.py`
Basic streaming endpoint for single operations:
- ETA streaming
- Route stops streaming
- Search results streaming

### 2. `/api/batch_stream.py`
Advanced streaming for batch operations:
- Batch ETA with progress tracking
- Nearby stops discovery
- Live updates with intervals

## Configuration

### vercel.json

```json
{
  "functions": {
    "api/stream.py": {
      "maxDuration": 300,  // 5 minutes for streaming
      "memory": 1024
    }
  },
  "headers": [
    {
      "source": "/stream",
      "headers": [
        {
          "key": "Content-Type",
          "value": "text/event-stream"
        },
        {
          "key": "Cache-Control",
          "value": "no-cache"
        },
        {
          "key": "Connection",
          "value": "keep-alive"
        }
      ]
    }
  ]
}
```

## Client-Side Usage

### JavaScript (Browser)

```javascript
const eventSource = new EventSource('/stream?action=eta&route_id=ROUTE_ID');

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
import json

url = 'https://your-domain.vercel.app/stream'
params = {'action': 'eta', 'route_id': 'ROUTE_ID'}

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
curl -N "https://your-domain.vercel.app/stream?action=eta&route_id=ROUTE_ID"
```

## Best Practices

### 1. Always Send Status Updates

```python
yield b'data: {"status": "started"}\n\n'
# ... process data ...
yield b'data: {"status": "complete"}\n\n'
```

### 2. Include Progress Information

```python
data = {
    "status": "processing",
    "current": idx + 1,
    "total": total,
    "progress_percent": int((idx + 1) / total * 100)
}
yield f'data: {json.dumps(data)}\n\n'.encode('utf-8')
```

### 3. Handle Errors Gracefully

```python
try:
    # Process data
    yield b'data: {"status": "success"}\n\n'
except Exception as e:
    error_data = json.dumps({"error": str(e)})
    yield f'data: {error_data}\n\n'.encode('utf-8')
```

### 4. Set Appropriate Headers

```python
self.start_response('200 OK', [
    ('Content-Type', 'text/event-stream'),
    ('Cache-Control', 'no-cache'),
    ('Connection', 'keep-alive'),
    ('X-Accel-Buffering', 'no'),  # Disable nginx buffering
])
```

### 5. Use WSGI Application Pattern

```python
def application(environ, start_response):
    """WSGI application entry point."""
    return handler(environ, start_response)
```

## Advantages of Streaming

1. **Real-time Feedback**: Users see progress immediately
2. **Better UX**: No waiting for entire response
3. **Memory Efficient**: Process data incrementally
4. **Extended Runtime**: Vercel supports longer durations for streaming
5. **Enhanced Logging**: Extended runtime logs show real-time output

## Testing

### Local Testing

```bash
# Start local server
python run_local.py

# Test streaming endpoint
curl -N "http://localhost:8000/stream?action=eta&route_id=ROUTE_ID"
```

### Automated Tests

```bash
# Run streaming tests
python test_streaming.py

# Run specific test
python test_streaming.py eta
```

## Debugging

### Check Response Format

```bash
curl -N "http://localhost:8000/stream?action=eta&route_id=ROUTE_ID" -v
```

### Monitor Logs

Vercel streaming functions provide extended runtime logs showing:
- Real-time function output
- Streaming progress
- Error details
- Performance metrics

## Limitations

1. **Max Duration**: 300 seconds (5 minutes) on Vercel
2. **Memory**: 1024 MB default (configurable)
3. **Buffer Size**: Avoid very large individual messages
4. **Connection**: Client must support SSE (most modern browsers do)

## Resources

- [Vercel Python Runtime Docs](https://vercel.com/docs/functions/runtimes/python)
- [Server-Sent Events Specification](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [STREAMING_API.md](STREAMING_API.md) - Complete API reference

## Examples in This Project

1. **stream.py**: Basic streaming patterns
   - Progressive data delivery
   - Search result streaming
   - Route information streaming

2. **batch_stream.py**: Advanced patterns
   - Batch processing with progress
   - Geospatial queries
   - Live update intervals

3. **streaming_demo.html**: Browser demo
   - EventSource usage
   - Progress visualization
   - Error handling

4. **test_streaming.py**: Testing examples
   - Python client implementation
   - Automated testing
   - Response parsing
