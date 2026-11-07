#!/usr/bin/env python3
"""
Richmond AI Demo - Quick Demo Runner

Run the complete demo from sample data generation to API testing.
"""
import subprocess
import json
import time
import os
import sys
from pathlib import Path

def run_command(command, description, cwd=None):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            cwd=cwd
        )
        print(f"✅ {description} completed")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def main():
    """Run the complete Richmond AI demo"""
    
    print("🎯 Richmond AI Agent Demo")
    print("=" * 40)
    print()
    
    # Check if we're in the right directory
    if not Path("cli.py").exists():
        print("❌ Please run this from the richmond-ai-demo directory")
        sys.exit(1)
    
    # Set environment variables
    profile = os.getenv('AWS_PROFILE', 'personal')
    stage = os.getenv('STAGE', 'dev')
    
    print(f"📋 Configuration:")
    print(f"   AWS Profile: {profile}")
    print(f"   Stage: {stage}")
    print()
    
    # Step 1: Install dependencies
    print("📦 Step 1: Installing dependencies")
    run_command("pip install -r requirements.txt", "Installing Python dependencies")
    
    # Step 2: Deploy infrastructure
    print("\n🏗️ Step 2: Deploying AWS infrastructure")
    deploy_output = run_command(
        f"./deploy.sh {stage} {profile}", 
        "Deploying CDK stack",
        cwd="infrastructure"
    )
    
    if not deploy_output:
        print("❌ Deployment failed. Check AWS credentials and try again.")
        sys.exit(1)
    
    # Extract API URL from deploy output
    api_url = None
    for line in deploy_output.split('\n'):
        if 'API Endpoint:' in line:
            api_url = line.split(': ')[1].strip()
            break
    
    if not api_url:
        print("❌ Could not extract API URL from deployment output")
        sys.exit(1)
    
    print(f"✅ API deployed at: {api_url}")
    
    # Step 3: Seed sample data
    print("\n🌱 Step 3: Seeding sample data")
    time.sleep(5)  # Wait for API to be ready
    
    seed_result = run_command(
        f"curl -s -X POST {api_url}/seed-data",
        "Loading Richmond tech community data"
    )
    
    if seed_result:
        try:
            seed_data = json.loads(seed_result)
            print(f"✅ Loaded {seed_data.get('items', 0)} data items")
        except json.JSONDecodeError:
            print("⚠️ Data seeding may have succeeded but response was not JSON")
    
    # Step 4: Test the API
    print("\n🧪 Step 4: Testing the AI agent")
    
    test_queries = [
        "What's the next tech meetup in Richmond?",
        "Tell me about the Richmond Python group",
        "What companies are hiring in Richmond?",
        "Where can I find AWS events this month?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: {query}")
        
        test_result = run_command(
            f"python cli.py --api-url {api_url} ask \"{query}\"",
            f"Running test query {i}"
        )
        
        if test_result:
            print(f"   Response: {test_result.strip()}")
        else:
            print("   ❌ Query failed")
        
        time.sleep(2)  # Rate limiting
    
    # Step 5: Interactive demo
    print("\n🎉 Demo completed successfully!")
    print("=" * 40)
    print(f"API Endpoint: {api_url}")
    print()
    print("💡 Try these commands:")
    print(f"   python cli.py --api-url {api_url} ask 'Your question here'")
    print(f"   python cli.py --api-url {api_url} demo")
    print(f"   python cli.py --api-url {api_url} health")
    print()
    print("🌐 Or test directly with curl:")
    print(f"   curl -X POST {api_url}/ask -H 'Content-Type: application/json' -d '{{\"query\":\"What tech events are happening?\"}}'")
    print()
    
    # Ask if user wants to run interactive demo
    try:
        response = input("🎮 Run interactive demo now? (y/n): ")
        if response.lower() in ['y', 'yes']:
            run_command(
                f"python cli.py --api-url {api_url} demo",
                "Running interactive demo"
            )
    except KeyboardInterrupt:
        print("\n👋 Demo completed!")

if __name__ == '__main__':
    main()