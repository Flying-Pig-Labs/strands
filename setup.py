"""
Setup script for Richmond AI Agent

This script helps users set up their environment for running the agent.
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def check_aws_cli():
    """Check if AWS CLI is installed and configured"""
    try:
        result = subprocess.run(['aws', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ AWS CLI: {result.stdout.strip()}")
        
        # Check if configured
        result = subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                              capture_output=True, text=True, check=True)
        caller_info = json.loads(result.stdout)
        print(f"✅ AWS Account: {caller_info.get('Account', 'Unknown')}")
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        print("❌ AWS CLI not installed or not configured")
        print("   Install: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html")
        print("   Configure: aws configure")
        return False


def check_sam_cli():
    """Check if SAM CLI is installed"""
    try:
        result = subprocess.run(['sam', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ SAM CLI: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ SAM CLI not installed")
        print("   Install: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html")
        return False


def install_python_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    
    try:
        # Create virtual environment if it doesn't exist
        venv_path = Path('.venv')
        if not venv_path.exists():
            print("Creating virtual environment...")
            subprocess.run([sys.executable, '-m', 'venv', '.venv'], check=True)
        
        # Determine activation script path
        if os.name == 'nt':  # Windows
            activate_script = venv_path / 'Scripts' / 'activate.bat'
            pip_executable = venv_path / 'Scripts' / 'pip.exe'
        else:  # Unix/Linux/macOS
            activate_script = venv_path / 'bin' / 'activate'
            pip_executable = venv_path / 'bin' / 'pip'
        
        # Install dependencies
        print("Installing requirements...")
        subprocess.run([str(pip_executable), 'install', '-r', 'requirements.txt'], check=True)
        
        print("✅ Python dependencies installed")
        print(f"   Virtual environment: {venv_path.absolute()}")
        print(f"   Activate with: source {activate_script}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False


def check_environment_variables():
    """Check for required environment variables"""
    print("\n🔐 Checking environment variables...")
    
    required_vars = {
        'ANTHROPIC_API_KEY': 'Anthropic API key for Claude integration'
    }
    
    optional_vars = {
        'AWS_PROFILE': 'AWS profile to use (optional)',
        'AWS_REGION': 'AWS region (default: us-east-1)'
    }
    
    missing_required = []
    
    for var, description in required_vars.items():
        if os.getenv(var):
            print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Not set ({description})")
            missing_required.append(var)
    
    for var, description in optional_vars.items():
        if os.getenv(var):
            print(f"✅ {var}: {os.getenv(var)}")
        else:
            print(f"⚠️  {var}: Not set ({description})")
    
    if missing_required:
        print(f"\n⚠️  Missing required environment variables: {', '.join(missing_required)}")
        print("\nSet them in your shell:")
        for var in missing_required:
            print(f"   export {var}='your-value-here'")
        return False
    
    return True


def create_env_template():
    """Create .env template file"""
    env_template = """# Richmond AI Agent Environment Variables
# Copy this file to .env and fill in your values

# Required: Anthropic API key
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Optional: AWS configuration
AWS_PROFILE=default
AWS_REGION=us-east-1

# Optional: Agent configuration
MODEL_NAME=claude-3-5-sonnet-20241022
DYNAMODB_TABLE=richmond-data

# Optional: API configuration (for CLI)
RICHMOND_AGENT_API=https://your-api-gateway-url.amazonaws.com/prod
"""
    
    env_file = Path('.env.template')
    with open(env_file, 'w') as f:
        f.write(env_template)
    
    print(f"📝 Created environment template: {env_file}")
    print("   Copy to .env and fill in your values")


def run_local_test():
    """Ask user if they want to run local tests"""
    response = input("\n🧪 Run local tests? (y/N): ").lower().strip()
    
    if response in ['y', 'yes']:
        print("Running local tests...")
        try:
            # Use the virtual environment Python if available
            venv_python = Path('.venv/bin/python')
            if venv_python.exists():
                python_cmd = str(venv_python)
            else:
                python_cmd = sys.executable
            
            subprocess.run([python_cmd, 'test_local.py'], check=True)
            return True
        except subprocess.CalledProcessError:
            print("❌ Local tests failed")
            return False
    
    return True


def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("🎉 Setup Complete!")
    print("="*60)
    print("\n📋 Next Steps:\n")
    
    print("1. Set up environment variables:")
    print("   cp .env.template .env")
    print("   # Edit .env with your API keys")
    print()
    
    print("2. Test locally:")
    print("   python test_local.py")
    print()
    
    print("3. Deploy to AWS:")
    print("   ./deploy.sh --stage dev --api-key YOUR_ANTHROPIC_API_KEY")
    print()
    
    print("4. Test the deployed API:")
    print("   python cli.py --api-endpoint YOUR_API_URL health")
    print("   python cli.py --api-endpoint YOUR_API_URL ask 'What meetups are in Richmond?'")
    print()
    
    print("📚 Documentation:")
    print("   README.md - Full documentation")
    print("   cli.py --help - CLI usage")
    print("   ./deploy.sh --help - Deployment options")
    print()
    
    print("🆘 Need help?")
    print("   Check the README.md file for troubleshooting")
    print("   Run with --debug for verbose output")


def main():
    """Main setup function"""
    print("🚀 Richmond AI Agent Setup")
    print("="*40)
    print("This script will help you set up the environment for the agent.\n")
    
    # Check all prerequisites
    checks = [
        ("Python Version", check_python_version),
        ("AWS CLI", check_aws_cli),
        ("SAM CLI", check_sam_cli),
    ]
    
    print("🔍 Checking prerequisites...")
    all_good = True
    
    for name, check_func in checks:
        if not check_func():
            all_good = False
    
    if not all_good:
        print("\n❌ Some prerequisites are missing. Please install them and run setup again.")
        sys.exit(1)
    
    # Install dependencies
    if not install_python_dependencies():
        print("\n❌ Failed to install dependencies.")
        sys.exit(1)
    
    # Check environment variables
    env_ok = check_environment_variables()
    
    # Create environment template
    create_env_template()
    
    # Run local tests if requested
    if env_ok:
        run_local_test()
    
    # Print next steps
    print_next_steps()
    
    if not env_ok:
        print("\n⚠️  Don't forget to set up your environment variables!")
        sys.exit(1)
    
    print("\n✅ Setup completed successfully!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)