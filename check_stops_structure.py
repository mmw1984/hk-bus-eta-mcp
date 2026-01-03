#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'c:/Users/mmw1984/Downloads/hk-transport-mcp-updated')

from hk_bus_eta import HKEta

hketa = HKEta()
route_id = "20+1+San Po Kong+Tsz Wan Shan (North) (Circular)"
route_info = hketa.route_list.get(route_id)

print(f"Route ID: {route_id}")
print(f"\nRoute info keys: {route_info.keys()}")
print(f"\nStops type: {type(route_info.get('stops'))}")
print(f"\nStops structure:")
print(json.dumps(route_info.get('stops'), ensure_ascii=False, indent=2)[:500])
