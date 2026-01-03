#!/usr/bin/env python3
"""
Test script for streaming endpoints

This script demonstrates how to consume streaming responses from the API.
"""

import sys
import json
import time
from urllib.parse import urlencode
from urllib.request import urlopen


def test_stream_eta():
    """Test streaming ETA endpoint."""
    print("\n=== Testing Stream ETA ===\n")
    
    params = {
        'action': 'eta',
        'route_id': '1+1+CHUK YUEN ESTATE+STAR FERRY',
        'seq': 0,
        'language': 'en'
    }
    
    # For local testing, use localhost:8000
    # For production, use your Vercel URL
    base_url = "http://localhost:8000/stream"
    url = f"{base_url}?{urlencode(params)}"
    
    print(f"Connecting to: {url}\n")
    
    try:
        with urlopen(url) as response:
            for line in response:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    print(f"Received: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    
                    if data.get('status') == 'complete':
                        break
    except Exception as e:
        print(f"Error: {e}")


def test_stream_stops():
    """Test streaming route stops endpoint."""
    print("\n=== Testing Stream Route Stops ===\n")
    
    params = {
        'action': 'stops',
        'route_id': '1+1+CHUK YUEN ESTATE+STAR FERRY',
        'language': 'en'
    }
    
    base_url = "http://localhost:8000/stream"
    url = f"{base_url}?{urlencode(params)}"
    
    print(f"Connecting to: {url}\n")
    
    try:
        with urlopen(url) as response:
            count = 0
            for line in response:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    
                    if data.get('status') == 'complete':
                        print(f"\nTotal stops received: {count}")
                        break
                    elif 'stop_id' in data:
                        count += 1
                        print(f"Stop {count}: {data.get('name')} (ID: {data.get('stop_id')})")
    except Exception as e:
        print(f"Error: {e}")


def test_search_stream():
    """Test streaming search endpoint."""
    print("\n=== Testing Stream Search ===\n")
    
    params = {
        'action': 'search',
        'keyword': '962',
        'type': 'routes'
    }
    
    base_url = "http://localhost:8000/stream"
    url = f"{base_url}?{urlencode(params)}"
    
    print(f"Connecting to: {url}\n")
    print(f"Searching for routes containing '962'...\n")
    
    try:
        with urlopen(url) as response:
            count = 0
            for line in response:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    
                    if data.get('status') == 'complete':
                        print(f"\nTotal routes found: {count}")
                        break
                    elif 'route_id' in data:
                        count += 1
                        print(f"Route {count}: {data.get('route_id')}")
    except Exception as e:
        print(f"Error: {e}")


def test_batch_eta():
    """Test batch ETA streaming endpoint."""
    print("\n=== Testing Batch ETA ===\n")
    
    route_ids = [
        '1+1+CHUK YUEN ESTATE+STAR FERRY',
        '2+2+BAMBOO GROVE+STAR FERRY'
    ]
    
    params = {
        'mode': 'batch',
        'route_ids': ','.join(route_ids),
        'language': 'en'
    }
    
    base_url = "http://localhost:8000/batch"
    url = f"{base_url}?{urlencode(params)}"
    
    print(f"Connecting to: {url}\n")
    print(f"Fetching ETA for {len(route_ids)} routes...\n")
    
    try:
        with urlopen(url) as response:
            for line in response:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    
                    status = data.get('status')
                    if status == 'started':
                        print(f"Started processing {data.get('total')} routes")
                    elif status == 'processing':
                        print(f"Progress: {data.get('progress_percent')}% - Processing {data.get('route_id')}")
                    elif status == 'result':
                        print(f"Result for route {data.get('route_id')}: {len(data.get('etas', []))} ETAs")
                    elif status == 'complete':
                        print(f"\nCompleted! Processed {data.get('total_processed')} routes")
                        break
    except Exception as e:
        print(f"Error: {e}")


def test_nearby_stops():
    """Test nearby stops streaming endpoint."""
    print("\n=== Testing Nearby Stops ===\n")
    
    # Hong Kong Central coordinates
    params = {
        'mode': 'nearby',
        'lat': 22.2819,
        'lon': 114.1580,
        'radius': 0.5
    }
    
    base_url = "http://localhost:8000/batch"
    url = f"{base_url}?{urlencode(params)}"
    
    print(f"Connecting to: {url}\n")
    print(f"Finding stops near ({params['lat']}, {params['lon']}) within {params['radius']}km...\n")
    
    try:
        with urlopen(url) as response:
            count = 0
            for line in response:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    
                    status = data.get('status')
                    if status == 'found':
                        print(f"Found {data.get('count')} nearby stops\n")
                    elif status == 'stop_info':
                        count += 1
                        stop = data.get('stop', {})
                        print(f"Stop {count}: {stop.get('name_en')} ({stop.get('distance_km')}km away)")
                    elif status == 'complete':
                        print(f"\nCompleted! Found {count} stops")
                        break
    except Exception as e:
        print(f"Error: {e}")


def test_live_updates():
    """Test live updates streaming endpoint."""
    print("\n=== Testing Live Updates ===\n")
    
    params = {
        'mode': 'live',
        'route_id': '1+1+CHUK YUEN ESTATE+STAR FERRY',
        'duration': 60,
        'interval': 20
    }
    
    base_url = "http://localhost:8000/batch"
    url = f"{base_url}?{urlencode(params)}"
    
    print(f"Connecting to: {url}\n")
    print(f"Monitoring route for {params['duration']} seconds with {params['interval']}s intervals...\n")
    
    try:
        with urlopen(url) as response:
            for line in response:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    
                    status = data.get('status')
                    if status == 'update':
                        print(f"Update #{data.get('update_number')} at {data.get('elapsed_seconds')}s: "
                              f"{len(data.get('etas', []))} ETAs")
                    elif status == 'complete':
                        print(f"\nCompleted! Received {data.get('total_updates')} updates")
                        break
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Run all streaming tests."""
    print("=" * 60)
    print("HK Transport MCP - Streaming API Tests")
    print("=" * 60)
    
    tests = [
        ("Stream ETA", test_stream_eta),
        ("Stream Route Stops", test_stream_stops),
        ("Stream Search", test_search_stream),
        ("Batch ETA", test_batch_eta),
        ("Nearby Stops", test_nearby_stops),
        # Skip live updates by default as it takes time
        # ("Live Updates", test_live_updates),
    ]
    
    for name, test_func in tests:
        try:
            test_func()
            time.sleep(1)  # Brief pause between tests
        except KeyboardInterrupt:
            print("\n\nTests interrupted by user")
            break
        except Exception as e:
            print(f"\nTest '{name}' failed: {e}")
    
    print("\n" + "=" * 60)
    print("Tests completed")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        tests = {
            'eta': test_stream_eta,
            'stops': test_stream_stops,
            'search': test_search_stream,
            'batch': test_batch_eta,
            'nearby': test_nearby_stops,
            'live': test_live_updates,
        }
        
        if test_name in tests:
            tests[test_name]()
        else:
            print(f"Unknown test: {test_name}")
            print(f"Available tests: {', '.join(tests.keys())}")
    else:
        main()
