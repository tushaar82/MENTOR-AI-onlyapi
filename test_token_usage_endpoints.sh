#!/bin/bash

# Token Usage API Testing Script
# This script provides examples for testing all token usage endpoints

API_BASE_URL="http://localhost:8000"

echo "=== Token Usage API Testing Script ==="
echo ""
echo "Note: These endpoints require authentication. Replace YOUR_TOKEN with valid access tokens."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo -e "${YELLOW}Testing: $description${NC}"
    echo "Endpoint: $method $endpoint"
    
    if [ -n "$data" ]; then
        echo "Request Body: $data"
        response=$(curl -s -w "\n%{http_code}" -X $method "$API_BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer YOUR_TOKEN" \
            -d "$data")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$API_BASE_URL$endpoint" \
            -H "Authorization: Bearer YOUR_TOKEN")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo -e "${GREEN}✓ Success (HTTP $http_code)${NC}"
    else
        echo -e "${RED}✗ Failed (HTTP $http_code)${NC}"
    fi
    
    echo "Response: $response_body"
    echo "----------------------------------------"
    echo ""
}

# Test endpoints
echo "1. Get Student Token Usage"
test_endpoint "GET" "/api/token-usage/student/student_123?period=monthly" "" "Get token usage for a student"

echo "2. Get Student Token Limits"
test_endpoint "GET" "/api/token-usage/limits/student/student_123" "" "Get token limits for a student"

echo "3. Get Parent Token Usage Summary"
test_endpoint "GET" "/api/token-usage/parent?period=monthly" "" "Get token usage summary for parent"

echo "4. Get Parent Comprehensive Summary"
test_endpoint "GET" "/api/token-usage/summary/parent?period=monthly" "" "Get comprehensive summary for parent dashboard"

echo "5. Reset Daily Token Usage (Admin Only)"
test_endpoint "POST" "/api/token-usage/reset/daily/student_123" \
    '{"reason": "Manual reset for testing", "admin_id": "admin_123"}' \
    "Reset daily token usage (requires admin token)"

echo "=== Testing Complete ==="
echo ""
echo "To test with actual authentication:"
echo "1. Replace YOUR_TOKEN with a valid access token"
echo "2. For admin endpoints, use an admin token"
echo "3. Update student_id and parent_id as needed"
echo ""
echo "Example with real token:"
echo 'curl -X GET "http://localhost:8000/api/token-usage/student/REAL_STUDENT_ID" \'
echo '  -H "Authorization: Bearer REAL_ACCESS_TOKEN"'