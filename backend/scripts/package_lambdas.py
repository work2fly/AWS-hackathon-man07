#!/usr/bin/env python3
"""
Lambda Packaging Script
🏆 Breaking Barriers UK 2026 compliant

Packages Lambda functions with dependencies for deployment
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path

# Colors for output
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color

def print_success(msg):
    print(f"{GREEN}✅ {msg}{NC}")

def print_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{NC}")

def print_error(msg):
    print(f"{RED}❌ {msg}{NC}")

def create_lambda_package(function_name, handler_file, output_dir):
    """Create a Lambda deployment package"""
    print(f"\n📦 Packaging {function_name}...")
    
    # Create temp directory
    temp_dir = Path(f"/tmp/lambda_{function_name}")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)
    
    # Copy source code
    src_dir = Path(__file__).parent.parent / "src"
    
    # Copy all Python files from src
    for py_file in src_dir.rglob("*.py"):
        rel_path = py_file.relative_to(src_dir)
        dest_file = temp_dir / rel_path
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(py_file, dest_file)
    
    print(f"  Copied source files")
    
    # Install dependencies
    requirements_file = Path(__file__).parent.parent / "requirements-lambda.txt"
    if requirements_file.exists():
        print(f"  Installing dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "-r", str(requirements_file),
            "-t", str(temp_dir),
            "--quiet"
        ], check=True)
        print_success("Dependencies installed")
    
    # Create zip file
    output_path = Path(output_dir) / f"{function_name}.zip"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"  Creating zip file...")
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(temp_dir)
                zipf.write(file_path, arcname)
    
    # Get file size
    size_mb = output_path.stat().st_size / (1024 * 1024)
    
    # Check size limits
    if size_mb > 50:
        print_warning(f"Package size {size_mb:.1f}MB exceeds 50MB limit for inline editing")
    elif size_mb > 10:
        print_warning(f"Package size {size_mb:.1f}MB exceeds 10MB limit for zipped inline editing")
    
    print_success(f"Created {output_path} ({size_mb:.1f}MB)")
    
    # Cleanup
    shutil.rmtree(temp_dir)
    
    return output_path

def main():
    print("🏆 Breaking Barriers UK 2026 - Lambda Packaging")
    print("=" * 60)
    
    # Get project root
    script_dir = Path(__file__).parent
    backend_dir = script_dir.parent
    project_root = backend_dir.parent
    
    # Output directory
    output_dir = backend_dir / "lambda_packages"
    output_dir.mkdir(exist_ok=True)
    
    # Package API handlers
    packages = [
        ("api_handlers", "lambda_functions/api_handlers.py"),
        ("websocket_handlers", "lambda_functions/websocket_handlers.py"),
    ]
    
    success_count = 0
    for function_name, handler_file in packages:
        try:
            create_lambda_package(function_name, handler_file, output_dir)
            success_count += 1
        except Exception as e:
            print_error(f"Failed to package {function_name}: {e}")
    
    print("\n" + "=" * 60)
    if success_count == len(packages):
        print_success(f"All {success_count} Lambda packages created successfully!")
        print("\nNext steps:")
        print("1. Deploy with Terraform:")
        print("   cd terraform")
        print("   terraform apply")
        print("\n2. Test the API endpoints")
        print("\n3. Uncomment frontend code")
        return 0
    else:
        print_error(f"Only {success_count}/{len(packages)} packages created")
        return 1

if __name__ == "__main__":
    sys.exit(main())
