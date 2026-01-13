#!/usr/bin/env python3
"""
Lambda Packaging Script for AI Therapy Platform
🏆 Breaking Barriers UK 2026 compliant
Packages all Lambda functions with dependencies and new services
"""

import os
import shutil
import subprocess
import zipfile
from pathlib import Path
import sys

def get_size_mb(path):
    """Get size in MB"""
    if os.path.isfile(path):
        return os.path.getsize(path) / (1024 * 1024)
    else:
        total = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total += os.path.getsize(filepath)
        return total / (1024 * 1024)

def clean_directory(directory):
    """Clean unnecessary files from directory"""
    patterns_to_remove = [
        "*.pyc",
        "__pycache__",
        "*.dist-info",
        "tests",
        "pytest*",
        "moto*", 
        "hypothesis*",
        "*.egg-info"
    ]
    
    for root, dirs, files in os.walk(directory):
        # Remove files matching patterns
        for file in files:
            if any(file.endswith(pattern.replace('*', '')) or pattern.replace('*', '') in file 
                   for pattern in patterns_to_remove if '*' in pattern):
                try:
                    os.remove(os.path.join(root, file))
                except OSError:
                    pass
        
        # Remove directories matching patterns
        dirs_to_remove = []
        for dir_name in dirs:
            if any(pattern.replace('*', '') in dir_name 
                   for pattern in patterns_to_remove if '*' in pattern):
                dirs_to_remove.append(dir_name)
        
        for dir_name in dirs_to_remove:
            try:
                shutil.rmtree(os.path.join(root, dir_name))
                dirs.remove(dir_name)
            except (OSError, ValueError):
                pass

def create_init_files(directory):
    """Create __init__.py files for proper Python imports"""
    for root, dirs, files in os.walk(directory):
        init_file = os.path.join(root, '__init__.py')
        if not os.path.exists(init_file):
            Path(init_file).touch()

def package_lambda(function_name, backend_dir, build_dir, dist_dir):
    """Package a single Lambda function"""
    print(f"📦 Packaging {function_name}...")
    
    temp_dir = os.path.join(build_dir, function_name)
    zip_file = os.path.join(dist_dir, f"{function_name}.zip")
    src_dir = os.path.join(backend_dir, "src")
    
    # Create temporary directory
    os.makedirs(temp_dir, exist_ok=True)
    
    # Install dependencies
    print("  📥 Installing dependencies...")
    requirements_file = os.path.join(backend_dir, "requirements-lambda.txt")
    subprocess.run([
        sys.executable, "-m", "pip", "install", 
        "-r", requirements_file, 
        "-t", temp_dir, 
        "--quiet"
    ], check=True)
    
    # Copy source code
    print("  📁 Copying source code...")
    
    # Copy the specific Lambda handler
    handler_file = os.path.join(src_dir, "lambda_functions", f"{function_name}.py")
    shutil.copy2(handler_file, temp_dir)
    
    # Copy all service modules (including new red flag detection services)
    services_src = os.path.join(src_dir, "services")
    services_dst = os.path.join(temp_dir, "services")
    if os.path.exists(services_src):
        shutil.copytree(services_src, services_dst)
    
    # Copy other necessary modules
    modules_to_copy = ["data", "models", "utils", "config", "middleware"]
    for module in modules_to_copy:
        module_src = os.path.join(src_dir, module)
        module_dst = os.path.join(temp_dir, module)
        if os.path.exists(module_src):
            shutil.copytree(module_src, module_dst)
    
    # Create __init__.py files
    create_init_files(temp_dir)
    
    # Clean unnecessary files
    print("  🗑️  Removing unnecessary files...")
    clean_directory(temp_dir)
    
    # Create ZIP file
    print("  🗜️  Creating ZIP archive...")
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arc_name)
    
    # Check package sizes
    zip_size_mb = get_size_mb(zip_file)
    unzip_size_mb = get_size_mb(temp_dir)
    
    print(f"  ✅ Package created: {function_name}.zip")
    print(f"     📏 Zipped size: {zip_size_mb:.1f}MB")
    print(f"     📏 Unzipped size: {unzip_size_mb:.1f}MB")
    
    # Warn if approaching limits
    if zip_size_mb > 8:
        print("  ⚠️  Warning: Package size approaching 10MB limit for console editing")
    if unzip_size_mb > 45:
        print("  ⚠️  Warning: Package size approaching 50MB Lambda limit")
    
    # Clean up temp directory
    shutil.rmtree(temp_dir)
    
    return zip_size_mb, unzip_size_mb

def main():
    """Main packaging function"""
    print("🚀 Starting Lambda packaging for AI Therapy Platform")
    print("🏆 Breaking Barriers UK 2026 compliant")
    print("=" * 50)
    
    # Configuration
    backend_dir = Path(__file__).parent.parent.absolute()
    build_dir = backend_dir / "build"
    dist_dir = backend_dir / "dist"
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    build_dir.mkdir(exist_ok=True)
    dist_dir.mkdir(exist_ok=True)
    
    # Lambda functions to package
    lambda_functions = [
        "auth_handlers",
        "cognito_triggers",
        "protected_endpoints", 
        "session_handlers",
        "websocket_handlers"
    ]
    
    # Package each Lambda function
    results = {}
    for function in lambda_functions:
        try:
            zip_size, unzip_size = package_lambda(function, str(backend_dir), str(build_dir), str(dist_dir))
            results[function] = {"success": True, "zip_size": zip_size, "unzip_size": unzip_size}
        except Exception as e:
            print(f"  ❌ Failed to package {function}: {e}")
            results[function] = {"success": False, "error": str(e)}
        print()
    
    # Create deployment summary
    print("📋 Deployment Summary")
    print("=" * 20)
    print(f"Lambda packages created in: {dist_dir}")
    print()
    print("📦 Packaged Functions:")
    
    total_size = 0
    for function, result in results.items():
        if result["success"]:
            print(f"  ✅ {function}.zip ({result['zip_size']:.1f}MB)")
            total_size += result["zip_size"]
        else:
            print(f"  ❌ {function}.zip (FAILED: {result['error']})")
    
    print(f"\n📊 Total package size: {total_size:.1f}MB")
    
    print("\n🔧 New Services Included in All Packages:")
    print("  ✅ red_flag_detection_service.py - UKind charity pattern detection")
    print("  ✅ notification_service.py - Multi-channel notifications") 
    print("  ✅ red_flag_management_service.py - Case management workflows")
    print("  ✅ trauma_informed_response_service.py - UKind trauma-informed responses")
    
    print("\n🚀 Deployment Instructions:")
    print("1. Upload ZIP files to AWS Lambda functions via AWS Console or CLI")
    print("2. Update Lambda function code using AWS CLI:")
    print("   aws lambda update-function-code --function-name <function-name> --zip-file fileb://dist/<function-name>.zip")
    print("3. Or use Terraform to deploy with updated source_code_hash")
    
    print("\n⚠️  Important Notes:")
    print("• Keep packages under 50MB unzipped for Lambda limits")
    print("• Keep packages under 10MB zipped for console editing capability") 
    print("• All packages include the new red flag detection services")
    print("• Remember: AWS accounts terminate at 23:00 on 15th January 2026")
    
    print("\n🏆 Breaking Barriers UK 2026 compliant Lambda packages ready!")

if __name__ == "__main__":
    main()