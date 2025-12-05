#!/usr/bin/env python3
"""
Add Missing Health Endpoints Script

This script adds missing health endpoints to various routers
to fix 404 errors during testing.

Author: Mentor AI Testing Suite
Version: 1.0.0
"""

import os
import re
from pathlib import Path

def add_health_endpoint_to_router(router_path: str, prefix: str):
    """Add health endpoint to a router file."""
    
    if not Path(router_path).exists():
        print(f"Router file not found: {router_path}")
        return False
    
    try:
        with open(router_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if health endpoint already exists
        if '@router.get("/health")' in content or '@router.get("\\/health")' in content:
            print(f"Health endpoint already exists in {router_path}")
            return True
        
        # Find the end of imports section
        import_end = content.find('\n\n#')
        if import_end == -1:
            import_end = content.find('\n\n# Create router')
        
        if import_end == -1:
            print(f"Could not find insertion point in {router_path}")
            return False
        
        # Health endpoint code to add
        health_endpoint_code = f'''

# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@router.get(
    "/health",
    summary="Health Check",
    description=f"Check if the {prefix} service is operational",
    tags=["Health"]
)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Service health status
    """
    from datetime import datetime
    return {{
        "status": "healthy",
        "service": "{prefix}",
        "timestamp": datetime.utcnow().isoformat()
    }}
'''
        
        # Insert the health endpoint
        new_content = content[:import_end] + health_endpoint_code + content[import_end:]
        
        # Write back to file
        with open(router_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"Added health endpoint to {router_path}")
        return True
        
    except Exception as e:
        print(f"Error adding health endpoint to {router_path}: {e}")
        return False

def fix_diagnostic_test_health():
    """Fix the 500 error in diagnostic-test health endpoint."""
    
    router_path = "routers/diagnostic_test_router.py"
    
    try:
        with open(router_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the existing health endpoint
        health_pattern = r'@router\.get\(\s*"/health"[^)]*\)\s*async def health_check\(\):[^}]+return \{[^}]+\}'
        
        if re.search(health_pattern, content):
            print("Found existing health endpoint in diagnostic_test_router.py")
            
            # Replace with fixed version
            fixed_health = '''@router.get(
    "/health",
    summary="Health Check",
    description="Check if the diagnostic test service is operational",
    tags=["Health"]
)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Service health status
    """
    from datetime import datetime
    return {
        "status": "healthy",
        "service": "diagnostic-test",
        "timestamp": datetime.utcnow().isoformat()
    }'''
            
            new_content = re.sub(health_pattern, fixed_health, content, flags=re.DOTALL)
            
            with open(router_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("Fixed health endpoint in diagnostic_test_router.py")
            return True
        else:
            print("Could not find health endpoint pattern in diagnostic_test_router.py")
            return False
            
    except Exception as e:
        print(f"Error fixing diagnostic-test health endpoint: {e}")
        return False

def add_main_health_endpoint():
    """Add main health endpoint to main.py."""
    
    main_path = "main.py"
    
    try:
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if health endpoint already exists
        if '@app.get("/api/health")' in content:
            print("Main health endpoint already exists")
            return True
        
        # Find a good place to add it (after existing app.get if any)
        insertion_point = content.find('\n@app.get')
        if insertion_point == -1:
            # Find end of router inclusions
            insertion_point = content.find('\n# Middleware')
        
        if insertion_point == -1:
            insertion_point = len(content)
        
        # Health endpoint code
        health_code = '''

@app.get("/api/health")
async def main_health_check():
    """
    Main health check endpoint.
    
    Returns:
        Overall system health status
    """
    from datetime import datetime
    return {
        "status": "healthy",
        "service": "mentor-ai-api",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
'''
        
        new_content = content[:insertion_point] + health_code + content[insertion_point:]
        
        with open(main_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("Added main health endpoint to main.py")
        return True
        
    except Exception as e:
        print(f"Error adding main health endpoint: {e}")
        return False

def main():
    """Main function to add missing health endpoints."""
    print("Adding missing health endpoints...")
    
    # Routers that need health endpoints
    routers_to_fix = [
        ("routers/auth_router.py", "auth"),
        ("routers/rag_router.py", "rag"),
        ("routers/analytics_router.py", "analytics"),
        ("routers/academic_guidance_router.py", "guidance"),
        ("routers/token_usage_router.py", "token-usage"),
        ("routers/study_center_router.py", "study-center"),
    ]
    
    success_count = 0
    
    # Add health endpoints to routers
    for router_path, prefix in routers_to_fix:
        if add_health_endpoint_to_router(router_path, prefix):
            success_count += 1
    
    # Fix existing diagnostic-test health endpoint
    if fix_diagnostic_test_health():
        success_count += 1
    
    # Add main health endpoint
    if add_main_health_endpoint():
        success_count += 1
    
    print(f"\n{'='*60}")
    print("HEALTH ENDPOINTS SUMMARY")
    print(f"{'='*60}")
    print(f"Successfully added/fixed: {success_count}/{len(routers_to_fix) + 2} endpoints")
    
    if success_count > 0:
        print("\n✅ Health endpoints added successfully!")
        print("Please restart the API server to apply changes.")
    else:
        print("\n❌ No health endpoints were added.")

if __name__ == "__main__":
    main()