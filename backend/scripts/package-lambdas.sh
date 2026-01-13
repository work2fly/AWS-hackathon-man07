#!/bin/bash
# Lambda Packaging Script for AI Therapy Platform
# 🏆 Breaking Barriers UK 2026 compliant
# Packages all Lambda functions with dependencies and new services

set -e

echo "🚀 Starting Lambda packaging for AI Therapy Platform"
echo "🏆 Breaking Barriers UK 2026 compliant"
echo "=================================================="

# Configuration
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${BACKEND_DIR}/build"
DIST_DIR="${BACKEND_DIR}/dist"
SRC_DIR="${BACKEND_DIR}/src"
TERRAFORM_DIR="$(cd "${BACKEND_DIR}/.." && pwd)/terraform"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf "${BUILD_DIR}" "${DIST_DIR}"
mkdir -p "${BUILD_DIR}" "${DIST_DIR}"

# Lambda functions to package
LAMBDA_FUNCTIONS=(
    "auth_handlers"
    "cognito_triggers" 
    "protected_endpoints"
    "session_handlers"
    "websocket_handlers"
)

# Function to create Lambda package
package_lambda() {
    local function_name=$1
    local temp_dir="${BUILD_DIR}/${function_name}"
    local zip_file="${DIST_DIR}/${function_name}.zip"
    
    echo "📦 Packaging ${function_name}..."
    
    # Create temporary directory
    mkdir -p "${temp_dir}"
    
    # Install dependencies
    echo "  📥 Installing dependencies..."
    pip install -r "${BACKEND_DIR}/requirements.txt" -t "${temp_dir}" --quiet
    
    # Copy source code
    echo "  📁 Copying source code..."
    
    # Copy the specific Lambda handler
    cp "${SRC_DIR}/lambda_functions/${function_name}.py" "${temp_dir}/"
    
    # Copy all service modules (including new red flag detection services)
    cp -r "${SRC_DIR}/services" "${temp_dir}/"
    
    # Copy data access layer
    cp -r "${SRC_DIR}/data" "${temp_dir}/"
    
    # Copy models
    cp -r "${SRC_DIR}/models" "${temp_dir}/"
    
    # Copy utilities
    cp -r "${SRC_DIR}/utils" "${temp_dir}/"
    
    # Copy configuration
    cp -r "${SRC_DIR}/config" "${temp_dir}/"
    
    # Copy middleware
    cp -r "${SRC_DIR}/middleware" "${temp_dir}/"
    
    # Create __init__.py files for proper Python imports
    find "${temp_dir}" -type d -exec touch {}/__init__.py \;
    
    # Remove unnecessary files to reduce package size
    echo "  🗑️  Removing unnecessary files..."
    find "${temp_dir}" -name "*.pyc" -delete
    find "${temp_dir}" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find "${temp_dir}" -name "*.dist-info" -type d -exec rm -rf {} + 2>/dev/null || true
    find "${temp_dir}" -name "tests" -type d -exec rm -rf {} + 2>/dev/null || true
    
    # Remove development dependencies not needed in Lambda
    rm -rf "${temp_dir}/pytest"* 2>/dev/null || true
    rm -rf "${temp_dir}/moto"* 2>/dev/null || true
    rm -rf "${temp_dir}/hypothesis"* 2>/dev/null || true
    
    # Create ZIP file
    echo "  🗜️  Creating ZIP archive..."
    cd "${temp_dir}"
    zip -r "${zip_file}" . -q
    cd - > /dev/null
    
    # Check package size (Lambda limit is 50MB unzipped, 10MB zipped for console editing)
    local zip_size=$(du -h "${zip_file}" | cut -f1)
    local unzip_size=$(du -sh "${temp_dir}" | cut -f1)
    
    echo "  ✅ Package created: ${function_name}.zip"
    echo "     📏 Zipped size: ${zip_size}"
    echo "     📏 Unzipped size: ${unzip_size}"
    
    # Warn if approaching limits
    local zip_size_mb=$(du -m "${zip_file}" | cut -f1)
    if [ "${zip_size_mb}" -gt 8 ]; then
        echo "  ⚠️  Warning: Package size approaching 10MB limit for console editing"
    fi
    
    # Clean up temp directory
    rm -rf "${temp_dir}"
}

# Package each Lambda function
for function in "${LAMBDA_FUNCTIONS[@]}"; do
    package_lambda "${function}"
    echo ""
done

# Create deployment summary
echo "📋 Deployment Summary"
echo "===================="
echo "Lambda packages created in: ${DIST_DIR}"
echo ""
echo "📦 Packaged Functions:"
SUCCESSFUL_PACKAGES=()
for function in "${LAMBDA_FUNCTIONS[@]}"; do
    if [ -f "${DIST_DIR}/${function}.zip" ]; then
        local size=$(du -h "${DIST_DIR}/${function}.zip" | cut -f1)
        echo "  ✅ ${function}.zip (${size})"
        SUCCESSFUL_PACKAGES+=("${function}")
    else
        echo "  ❌ ${function}.zip (FAILED)"
    fi
done

# Copy successful packages to terraform directory
if [ ${#SUCCESSFUL_PACKAGES[@]} -gt 0 ] && [ -d "${TERRAFORM_DIR}" ]; then
    echo ""
    echo "📁 Copying ZIP files to Terraform directory: ${TERRAFORM_DIR}"
    COPIED_FILES=()
    for function in "${SUCCESSFUL_PACKAGES[@]}"; do
        if cp "${DIST_DIR}/${function}.zip" "${TERRAFORM_DIR}/${function}.zip" 2>/dev/null; then
            echo "  ✅ Copied ${function}.zip"
            COPIED_FILES+=("${function}.zip")
        else
            echo "  ❌ Failed to copy ${function}.zip"
        fi
    done
    
    if [ ${#COPIED_FILES[@]} -gt 0 ]; then
        echo ""
        echo "🎯 Ready for Terraform deployment!"
        echo "   All ${#COPIED_FILES[@]} ZIP files copied to terraform/ directory"
    else
        echo ""
        echo "⚠️  No files copied to terraform directory"
    fi
elif [ ! -d "${TERRAFORM_DIR}" ]; then
    echo ""
    echo "⚠️  Terraform directory not found: ${TERRAFORM_DIR}"
    echo "   ZIP files available in dist/ directory only"
else
    echo ""
    echo "⚠️  No successful packages to copy"
fi

echo ""
echo "🔧 New Services Included in All Packages:"
echo "  ✅ red_flag_detection_service.py - UKind charity pattern detection"
echo "  ✅ notification_service.py - Multi-channel notifications"
echo "  ✅ red_flag_management_service.py - Case management workflows"
echo "  ✅ trauma_informed_response_service.py - UKind trauma-informed responses"

echo ""
echo "🚀 Deployment Instructions:"
echo "1. ZIP files automatically copied to terraform/ directory"
echo "2. Run 'terraform apply' from terraform/ directory"
echo "3. Or update Lambda function code using AWS CLI:"
echo "   aws lambda update-function-code --function-name <function-name> --zip-file fileb://<function-name>.zip"
echo "4. Or use Terraform with updated source_code_hash (auto-detected)"

echo ""
echo "⚠️  Important Notes:"
echo "• Keep packages under 50MB unzipped for Lambda limits"
echo "• Keep packages under 10MB zipped for console editing capability"
echo "• All packages include the new red flag detection services"
echo "• Remember: AWS accounts terminate at 23:00 on 15th January 2026"

echo ""
echo "🏆 Breaking Barriers UK 2026 compliant Lambda packages ready!"