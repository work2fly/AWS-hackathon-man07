#!/bin/bash

# Integration Testing Script
# 🏆 Breaking Barriers UK 2026 compliant
#
# Tests the complete frontend-backend integration

set -e

echo "🏆 Breaking Barriers UK 2026 - Integration Testing"
echo "==================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="https://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev"
WS_URL="wss://yqv4v90gj9.execute-api.us-west-2.amazonaws.com/dev"

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Function to print test result
print_test_result() {
    local test_name=$1
    local result=$2
    
    if [ "$result" = "PASS" ]; then
        echo -e "${GREEN}✅ PASS${NC} - $test_name"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC} - $test_name"
        ((TESTS_FAILED++))
    fi
}

# Function to test API endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local token=$3
    local data=$4
    
    if [ -n "$token" ]; then
        if [ -n "$data" ]; then
            response=$(curl -s -w "\n%{http_code}" -X "$method" "${API_URL}${endpoint}" \
                -H "Authorization: Bearer $token" \
                -H "Content-Type: application/json" \
                -d "$data")
        else
            response=$(curl -s -w "\n%{http_code}" -X "$method" "${API_URL}${endpoint}" \
                -H "Authorization: Bearer $token")
        fi
    else
        if [ -n "$data" ]; then
            response=$(curl -s -w "\n%{http_code}" -X "$method" "${API_URL}${endpoint}" \
                -H "Content-Type: application/json" \
                -d "$data")
        else
            response=$(curl -s -w "\n%{http_code}" -X "$method" "${API_URL}${endpoint}")
        fi
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    echo "$http_code"
}

echo "Test Suite 1: Configuration Verification"
echo "========================================="
echo ""

# Test 1: Check if Cognito config exists
if [ -f "backend/cognito-frontend-config.json" ]; then
    print_test_result "Cognito configuration file exists" "PASS"
    
    CLIENT_ID=$(jq -r '.userPoolWebClientId' backend/cognito-frontend-config.json)
    USER_POOL_ID=$(jq -r '.userPoolId' backend/cognito-frontend-config.json)
    
    echo "  Client ID: $CLIENT_ID"
    echo "  User Pool ID: $USER_POOL_ID"
else
    print_test_result "Cognito configuration file exists" "FAIL"
fi

# Test 2: Check if frontend .env.local exists
if [ -f "ai-therapy-frontend/.env.local" ]; then
    print_test_result "Frontend environment file exists" "PASS"
else
    print_test_result "Frontend environment file exists" "FAIL"
fi

# Test 3: Check if backend .env exists
if [ -f "backend/.env" ]; then
    print_test_result "Backend environment file exists" "PASS"
else
    print_test_result "Backend environment file exists" "FAIL"
fi

# Test 4: Check if Lambda packages exist
if [ -f "backend/lambda_packages/api_handlers.zip" ]; then
    print_test_result "API handlers package exists" "PASS"
    
    size=$(du -h backend/lambda_packages/api_handlers.zip | cut -f1)
    echo "  Package size: $size"
else
    print_test_result "API handlers package exists" "FAIL"
fi

echo ""
echo "Test Suite 2: AWS Resources"
echo "==========================="
echo ""

# Test 5: Check if Cognito User Pool exists
if aws cognito-idp describe-user-pool --user-pool-id us-west-2_ASOPUuOOV --region us-west-2 &>/dev/null; then
    print_test_result "Cognito User Pool exists" "PASS"
else
    print_test_result "Cognito User Pool exists" "FAIL"
fi

# Test 6: Check if Lambda function exists
if aws lambda get-function --function-name ai-therapy-platform-dev-api-handlers --region us-west-2 &>/dev/null; then
    print_test_result "API handlers Lambda function exists" "PASS"
else
    print_test_result "API handlers Lambda function exists" "FAIL"
    echo -e "${YELLOW}  Note: Run 'cd terraform && terraform apply' to deploy${NC}"
fi

# Test 7: Check if API Gateway exists
if aws apigatewayv2 get-api --api-id yqv4v90gj9 --region us-west-2 &>/dev/null; then
    print_test_result "API Gateway exists" "PASS"
else
    print_test_result "API Gateway exists" "FAIL"
fi

# Test 8: Check DynamoDB tables
tables=("users" "sessions" "redflags" "notifications")
for table in "${tables[@]}"; do
    table_name="ai-therapy-platform-dev-${table}"
    if aws dynamodb describe-table --table-name "$table_name" --region us-west-2 &>/dev/null; then
        print_test_result "DynamoDB table: $table" "PASS"
    else
        print_test_result "DynamoDB table: $table" "FAIL"
    fi
done

echo ""
echo "Test Suite 3: API Endpoints (Basic)"
echo "===================================="
echo ""

# Test 9: Test API Gateway health (OPTIONS request)
http_code=$(test_endpoint "OPTIONS" "/auth/profile" "" "")
if [ "$http_code" = "200" ] || [ "$http_code" = "204" ]; then
    print_test_result "API Gateway CORS (OPTIONS /auth/profile)" "PASS"
else
    print_test_result "API Gateway CORS (OPTIONS /auth/profile)" "FAIL"
    echo "  HTTP Code: $http_code"
fi

echo ""
echo "Test Suite 4: Frontend Configuration"
echo "====================================="
echo ""

# Test 10: Check if aws-config.ts has correct client ID
if [ -f "ai-therapy-frontend/src/config/aws-config.ts" ]; then
    if grep -q "$CLIENT_ID" "ai-therapy-frontend/src/config/aws-config.ts" 2>/dev/null; then
        print_test_result "Frontend aws-config.ts has correct client ID" "PASS"
    else
        print_test_result "Frontend aws-config.ts has correct client ID" "FAIL"
    fi
else
    print_test_result "Frontend aws-config.ts exists" "FAIL"
fi

# Test 11: Check if USE_MOCK_AUTH is false
if [ -f "ai-therapy-frontend/src/services/auth.ts" ]; then
    if grep -q "const USE_MOCK_AUTH = false" "ai-therapy-frontend/src/services/auth.ts" 2>/dev/null; then
        print_test_result "Real authentication enabled (USE_MOCK_AUTH = false)" "PASS"
    else
        print_test_result "Real authentication enabled (USE_MOCK_AUTH = false)" "FAIL"
        echo -e "${YELLOW}  Note: Run './integrate.sh' to enable real auth${NC}"
    fi
else
    print_test_result "Frontend auth.ts exists" "FAIL"
fi

# Test 12: Check if frontend dependencies are installed
if [ -d "ai-therapy-frontend/node_modules" ]; then
    print_test_result "Frontend dependencies installed" "PASS"
else
    print_test_result "Frontend dependencies installed" "FAIL"
    echo -e "${YELLOW}  Note: Run 'cd ai-therapy-frontend && npm install'${NC}"
fi

echo ""
echo "Test Suite 5: Documentation"
echo "==========================="
echo ""

# Test 13: Check if integration documentation exists
docs=(
    "FRONTEND_BACKEND_INTEGRATION_GUIDE.md"
    "INTEGRATION_QUICK_START.md"
    "INTEGRATION_COMPLETE_SUMMARY.md"
    "DEPLOYMENT_GUIDE.md"
)

for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        print_test_result "Documentation: $doc" "PASS"
    else
        print_test_result "Documentation: $doc" "FAIL"
    fi
done

echo ""
echo "=========================================="
echo "Test Results Summary"
echo "=========================================="
echo ""
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "Next Steps:"
    echo "----------"
    echo "1. Start the frontend:"
    echo "   cd ai-therapy-frontend"
    echo "   npm run dev"
    echo ""
    echo "2. Open http://localhost:3000"
    echo ""
    echo "3. Test the integration:"
    echo "   - Register a new user"
    echo "   - Login with credentials"
    echo "   - Start a therapy session"
    echo "   - Check therapist dashboard"
    echo "   - Check admin dashboard"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed${NC}"
    echo ""
    echo "Common fixes:"
    echo "------------"
    echo "1. Run integration script:"
    echo "   ./integrate.sh"
    echo ""
    echo "2. Package Lambda functions:"
    echo "   cd backend"
    echo "   python3 scripts/package_lambdas.py"
    echo ""
    echo "3. Deploy infrastructure:"
    echo "   cd terraform"
    echo "   terraform apply"
    echo ""
    echo "4. Install frontend dependencies:"
    echo "   cd ai-therapy-frontend"
    echo "   npm install"
    echo ""
    exit 1
fi
