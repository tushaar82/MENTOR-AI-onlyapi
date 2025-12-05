#!/usr/bin/env python3
"""
Analyze Missing Endpoints Script

This script analyzes the router files to identify which endpoints are actually
implemented and compares them with the test endpoints to find missing ones.

Author: Mentor AI Testing Suite
Version: 1.0.0
"""

import os
import re
import json
from typing import Dict, List, Set
from pathlib import Path

def extract_endpoints_from_router(router_path: str) -> List[Dict]:
    """Extract endpoint information from a router file."""
    endpoints = []
    
    try:
        with open(router_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find router prefix
        prefix_match = re.search(r'router\s*=\s*APIRouter\(\s*prefix=["\']([^"\']+)["\']', content)
        prefix = prefix_match.group(1) if prefix_match else ""
        
        # Find all @router decorators
        router_patterns = [
            r'@router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
            r'@router\.(get|post|put|delete|patch)\s*\(',
        ]
        
        for pattern in router_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                method = match.group(1).upper()
                
                # Extract path from the decorator
                if len(match.groups()) > 1:
                    path = match.group(2)
                else:
                    # Look for path in the next few lines
                    start_pos = match.end()
                    next_lines = content[start_pos:start_pos + 200]
                    path_match = re.search(r'["\']([^"\']+)["\']', next_lines)
                    path = path_match.group(1) if path_match else "/"
                
                full_path = prefix + path
                
                endpoints.append({
                    "method": method,
                    "path": full_path,
                    "router_file": router_path.name,
                    "prefix": prefix
                })
    
    except Exception as e:
        print(f"Error processing {router_path}: {e}")
    
    return endpoints

def extract_endpoints_from_main():
    """Extract endpoints directly defined in main.py."""
    endpoints = []
    main_path = Path("main.py")
    
    if not main_path.exists():
        return endpoints
    
    try:
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find @app decorators
        app_patterns = [
            r'@app\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in app_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                method = match.group(1).upper()
                path = match.group(2)
                
                endpoints.append({
                    "method": method,
                    "path": path,
                    "router_file": "main.py",
                    "prefix": ""
                })
    
    except Exception as e:
        print(f"Error processing main.py: {e}")
    
    return endpoints

def main():
    """Main function to analyze endpoints."""
    print("Analyzing implemented endpoints...")
    
    # Get all router files
    router_files = list(Path("routers").glob("*.py"))
    
    all_endpoints = []
    
    # Extract from routers
    for router_file in router_files:
        if router_file.name == "__init__.py":
            continue
        endpoints = extract_endpoints_from_router(router_file)
        all_endpoints.extend(endpoints)
    
    # Extract from main.py
    main_endpoints = extract_endpoints_from_main()
    all_endpoints.extend(main_endpoints)
    
    # Group endpoints by path and method
    endpoint_map = {}
    for endpoint in all_endpoints:
        key = (endpoint["path"], endpoint["method"])
        if key not in endpoint_map:
            endpoint_map[key] = []
        endpoint_map[key].append(endpoint)
    
    # Print summary
    print(f"\n{'='*60}")
    print("IMPLEMENTED ENDPOINTS SUMMARY")
    print(f"{'='*60}")
    print(f"Total endpoints found: {len(all_endpoints)}")
    print(f"Unique path-method combinations: {len(endpoint_map)}")
    
    # Group by router
    router_counts = {}
    for endpoint in all_endpoints:
        router = endpoint["router_file"]
        router_counts[router] = router_counts.get(router, 0) + 1
    
    print(f"\nEndpoints by router:")
    for router, count in sorted(router_counts.items()):
        print(f"  {router}: {count}")
    
    # Print all endpoints
    print(f"\n{'='*60}")
    print("ALL IMPLEMENTED ENDPOINTS")
    print(f"{'='*60}")
    
    sorted_endpoints = sorted(all_endpoints, key=lambda x: (x["path"], x["method"]))
    
    for endpoint in sorted_endpoints:
        print(f"{endpoint['method']:8} {endpoint['path']}")
    
    # Save to file
    output_data = {
        "summary": {
            "total_endpoints": len(all_endpoints),
            "unique_combinations": len(endpoint_map),
            "router_counts": router_counts
        },
        "endpoints": sorted_endpoints
    }
    
    with open("implemented_endpoints.json", 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nDetailed results saved to: implemented_endpoints.json")
    
    # Common test endpoints that might be missing
    common_test_endpoints = [
        "/api/health",
        "/api/auth/health",
        "/api/diagnostic-test/health",
        "/api/rag/health",
        "/api/analytics/health",
        "/api/guidance/health",
        "/api/token-usage/health",
        "/api/study-center/health",
        "/api/ai-features/health",
    ]
    
    print(f"\n{'='*60}")
    print("COMMON HEALTH ENDPOINTS CHECK")
    print(f"{'='*60}")
    
    implemented_paths = {endpoint["path"] for endpoint in all_endpoints}
    
    for health_endpoint in common_test_endpoints:
        if health_endpoint in implemented_paths:
            print(f"✓ {health_endpoint}")
        else:
            print(f"✗ {health_endpoint} - MISSING")
    
    return output_data

if __name__ == "__main__":
    main()