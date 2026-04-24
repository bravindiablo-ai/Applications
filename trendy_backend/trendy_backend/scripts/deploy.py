#!/usr/bin/env python3
"""
Production Deployment Script
"""

import os
import subprocess
import sys

def check_dependencies():
    """Check if all dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import fastapi
        import sqlalchemy
        import uvicorn
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def setup_production():
    """Setup production environment"""
    print("🚀 Setting up production environment...")
    
    # Set environment variables
    os.environ['ENVIRONMENT'] = 'production'
    os.environ['DEBUG'] = 'false'
    
    # Create production config
    config = {
        'host': '0.0.0.0',
        'port': 8000,
        'reload': False,
        'workers': 4
    }
    
    return config

def start_server(config):
    """Start the production server"""
    print("🌐 Starting production server...")
    
    cmd = [
        sys.executable, '-m', 'uvicorn',
        'app.main:app',
        '--host', config['host'],
        '--port', str(config['port']),
        '--workers', str(config['workers'])
    ]
    
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        return False

def run_tests():
    """Run comprehensive tests"""
    print("🧪 Running tests...")
    
    try:
        result = subprocess.run([
            sys.executable, 'scripts/test_endpoints.py'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All tests passed")
            return True
        else:
            print("❌ Tests failed")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

def main():
    """Main deployment process"""
    print("🎯 Starting deployment process...\n")
    
    # Check dependencies
    if not check_dependencies():
        print("Please install missing dependencies")
        return False
    
    # Run tests
    if not run_tests():
        print("Fix issues before deployment")
        return False
    
    # Setup production
    config = setup_production()
    
    # Start server
    print("\n🚀 Starting production server...")
    print("Server will be available at http://localhost:8000")
    print("Press Ctrl+C to stop")
    
    return start_server(config)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
