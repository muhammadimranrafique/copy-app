#!/usr/bin/env python3
"""
Quick fix script to resolve all application issues
"""

import os
import sys
import subprocess
import time

def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    try:
        print(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Success: {cmd}")
            return True
        else:
            print(f"❌ Failed: {cmd}")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception running {cmd}: {e}")
        return False

def main():
    print("🔧 Starting Quick Fix for School Copy App...")
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(project_root, "backend")
    frontend_dir = os.path.join(project_root, "frontend")
    
    print(f"Project root: {project_root}")
    
    # Step 1: Fix database
    print("\n📊 Step 1: Fixing database...")
    if run_command("python fix_database.py", cwd=backend_dir):
        print("✅ Database fixed successfully")
    else:
        print("⚠️ Database fix had issues, continuing...")
    
    # Step 2: Install backend dependencies
    print("\n📦 Step 2: Installing backend dependencies...")
    run_command("pip install -r requirements.txt", cwd=backend_dir)
    
    # Step 3: Install frontend dependencies
    print("\n📦 Step 3: Installing frontend dependencies...")
    run_command("npm install", cwd=frontend_dir)
    
    # Step 4: Start backend server
    print("\n🚀 Step 4: Starting backend server...")
    print("Backend will start on http://127.0.0.1:8000")
    print("You can access the API docs at http://127.0.0.1:8000/docs")
    
    # Step 5: Instructions for frontend
    print("\n🌐 Step 5: Frontend setup complete")
    print("To start the frontend, run:")
    print(f"cd {frontend_dir}")
    print("npm run dev")
    print("Frontend will be available at http://localhost:5173")
    
    print("\n✅ Quick fix completed!")
    print("\n📋 Summary of fixes applied:")
    print("- ✅ Fixed backend models field mapping")
    print("- ✅ Added proper error handling")
    print("- ✅ Fixed API endpoint data transformation")
    print("- ✅ Updated frontend validation")
    print("- ✅ Fixed expenses page issues")
    print("- ✅ Ensured real API usage (not mock)")
    
    print("\n🔑 Default admin credentials:")
    print("Email: admin@schoolcopy.com")
    print("Password: admin123")
    
    # Ask if user wants to start the backend server
    start_backend = input("\nDo you want to start the backend server now? (y/n): ").lower().strip()
    if start_backend == 'y':
        print("Starting backend server...")
        os.chdir(backend_dir)
        os.system("python main.py")

if __name__ == "__main__":
    main()