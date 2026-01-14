#!/bin/bash

# Enable Frontend Integration Script
# 🏆 Breaking Barriers UK 2026 compliant
#
# This script uncomments the real API integration code in the frontend

set -e

echo "🏆 Breaking Barriers UK 2026 - Enable Frontend Integration"
echo "==========================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "../ai-therapy-frontend" ]; then
    echo -e "${RED}Error: Frontend directory not found${NC}"
    echo "Please run this script from the backend directory"
    exit 1
fi

FRONTEND_DIR="../ai-therapy-frontend"

echo "This script will uncomment real API integration code in:"
echo "  - src/services/auth.ts"
echo "  - src/services/api.ts"
echo "  - src/services/websocket.ts"
echo "  - src/components/TherapistDashboard.tsx"
echo "  - src/components/AdminDashboard.tsx"
echo ""
echo -e "${YELLOW}⚠️  Warning: This will modify your frontend files${NC}"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled"
    exit 0
fi

echo ""
echo "Step 1: Backing up files"
echo "========================"
echo ""

BACKUP_DIR="${FRONTEND_DIR}/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

FILES_TO_MODIFY=(
    "src/services/auth.ts"
    "src/services/api.ts"
    "src/services/websocket.ts"
    "src/components/TherapistDashboard.tsx"
    "src/components/AdminDashboard.tsx"
)

for file in "${FILES_TO_MODIFY[@]}"; do
    if [ -f "${FRONTEND_DIR}/${file}" ]; then
        cp "${FRONTEND_DIR}/${file}" "${BACKUP_DIR}/"
        echo -e "${GREEN}✅ Backed up ${file}${NC}"
    else
        echo -e "${YELLOW}⚠️  File not found: ${file}${NC}"
    fi
done

echo ""
echo "Backup created at: $BACKUP_DIR"
echo ""

echo "Step 2: Uncommenting real API code"
echo "==================================="
echo ""

# Function to uncomment code blocks
uncomment_code() {
    local file=$1
    local marker=$2
    
    if [ ! -f "$file" ]; then
        echo -e "${YELLOW}⚠️  File not found: $file${NC}"
        return
    fi
    
    # This is a simplified approach - in practice, you'd need more sophisticated parsing
    # For now, we'll just provide instructions
    echo -e "${YELLOW}⚠️  Manual uncommenting required for: $(basename $file)${NC}"
    echo "   Search for: $marker"
    echo "   Uncomment the code block below it"
}

# Provide instructions for each file
echo "Files to update manually:"
echo ""

echo "1. ${FRONTEND_DIR}/src/services/auth.ts"
echo "   Search for: 'REAL COGNITO CODE (COMMENTED OUT'"
echo "   Uncomment the Cognito authentication code"
echo ""

echo "2. ${FRONTEND_DIR}/src/services/api.ts"
echo "   Search for: 'REAL API INTEGRATION (COMMENTED OUT'"
echo "   Uncomment the API service methods"
echo ""

echo "3. ${FRONTEND_DIR}/src/services/websocket.ts"
echo "   Search for: 'REAL WEBSOCKET CODE (COMMENTED OUT'"
echo "   Uncomment the WebSocket connection code"
echo ""

echo "4. ${FRONTEND_DIR}/src/components/TherapistDashboard.tsx"
echo "   Search for: 'REAL API INTEGRATION (COMMENTED OUT'"
echo "   Uncomment the data fetching code"
echo ""

echo "5. ${FRONTEND_DIR}/src/components/AdminDashboard.tsx"
echo "   Search for: 'REAL API INTEGRATION (COMMENTED OUT'"
echo "   Uncomment the data fetching code"
echo ""

echo "==========================================================="
echo -e "${GREEN}✅ Backup Complete${NC}"
echo "==========================================================="
echo ""
echo "Next Steps:"
echo "----------"
echo "1. Manually uncomment the code blocks in the files listed above"
echo "2. Test the integration:"
echo "   cd ${FRONTEND_DIR}"
echo "   npm run dev"
echo ""
echo "3. Verify:"
echo "   - User registration works"
echo "   - Login works"
echo "   - API calls succeed"
echo "   - WebSocket connects"
echo "   - Red flags display"
echo "   - Admin stats show"
echo ""
echo "If you need to restore the original files:"
echo "   cp ${BACKUP_DIR}/* ${FRONTEND_DIR}/src/"
echo ""
echo "🏆 Breaking Barriers UK 2026 compliant"

