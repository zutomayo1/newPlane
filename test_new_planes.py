#!/usr/bin/env python3
"""Quick test for the 3 new planes."""
import sys
from config import PLANES
from utils import get_plane_surf

print("=== Testing 3 New Planes ===\n")

for pid in ['eclipse', 'prism', 'necro']:
    try:
        plane_data = PLANES[pid]
        surf = get_plane_surf(pid, plane_data.get('visual'))
        
        print(f"✓ {pid}:")
        print(f"  Name: {plane_data['name']}")
        print(f"  HP: {plane_data['hp']}, Speed: {plane_data['speed']}, Damage: {plane_data['damage']}")
        print(f"  Bullet type: {plane_data['bullet_type']}")
        print(f"  Ultimate: {plane_data['ult_name']}")
        print(f"  Visual rendered: {surf.get_size()}\n")
    except Exception as e:
        print(f"✗ {pid}: ERROR - {e}\n")
        sys.exit(1)

print("=== All 3 new planes verified successfully! ===")
