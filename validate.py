#!/usr/bin/env python3
"""
Validation Script for Richmond AI Agent

This script validates the project setup and checks all components
are working correctly before deployment.
"""

import os
import sys
import json
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Colors for output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{title.center(60)}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}\n")


def print_check(name: str, passed: bool, details: str = ""):
    """Print a check result"""
    icon = f"{Colors.GREEN}✅" if passed else f"{Colors.RED}❌"
    status = f"{Colors.GREEN}PASS" if passed else f"{Colors.RED}FAIL"
    print(f"{icon} {name:<40} [{status}{Colors.END}]")
    if details:
        print(f"   {Colors.CYAN}{details}{Colors.END}")


class ProjectValidator:
    """Validates the Richmond AI Agent project setup"""
    
    def __init__(self):
        self.results = {}
        self.required_files = [
            'agent.py',
            'lambda_handler.py', 
            'cli.py',
            'requirements.txt',
            'template.yaml',
            'load_sample_data.py',
            'deploy.sh',
            'setup.py',
            'test_local.py'
        ]
        
    def validate_file_structure(self) -> Tuple[bool, str]:
        """Validate required files exist"""
        missing_files = []
        
        for file in self.required_files:
            if not Path(file).exists():
                missing_files.append(file)
        
        if missing_files:
            return False, f"Missing files: {', '.join(missing_files)}"
        
        return True, f"All {len(self.required_files)} required files present"
    
    def validate_python_syntax(self) -> Tuple[bool, str]:
        """Validate Python files have correct syntax"""
        python_files = [f for f in self.required_files if f.endswith('.py')]
        errors = []
        
        for file in python_files:
            try:
                with open(file, 'r') as f:
                    compile(f.read(), file, 'exec')
            except SyntaxError as e:
                errors.append(f"{file}: Line {e.lineno} - {e.msg}")
            except Exception as e:
                errors.append(f"{file}: {str(e)}")
        
        if errors:
            return False, f"Syntax errors: {'; '.join(errors)}"
        
        return True, f"All {len(python_files)} Python files have valid syntax"
    
    def validate_dependencies(self) -> Tuple[bool, str]:
        """Validate required dependencies can be imported"""
        required_imports = [
            ('boto3', 'AWS SDK'),
            ('click', 'CLI framework'),
            ('rich', 'Rich console output'),
            ('pydantic', 'Data validation'),
            ('httpx', 'HTTP client')
        ]
        
        missing_deps = []
        
        for module, description in required_imports:
            try:
                __import__(module)
            except ImportError:
                missing_deps.append(f"{module} ({description})")
        
        if missing_deps:
            return False, f"Missing dependencies: {', '.join(missing_deps)}"
        
        return True, f"All {len(required_imports)} key dependencies available"
    
    def validate_environment_variables(self) -> Tuple[bool, str]:
        """Validate environment variables"""
        required_vars = ['ANTHROPIC_API_KEY']
        optional_vars = ['AWS_PROFILE', 'AWS_REGION']
        
        missing_required = []
        set_optional = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_required.append(var)
        
        for var in optional_vars:
            if os.getenv(var):
                set_optional.append(var)
        
        if missing_required:
            return False, f"Missing required: {', '.join(missing_required)}"
        
        optional_info = f", Optional set: {', '.join(set_optional)}" if set_optional else ""
        return True, f"Required environment variables set{optional_info}"
    
    def validate_aws_setup(self) -> Tuple[bool, str]:
        """Validate AWS CLI configuration"""
        try:
            # Check AWS CLI is installed
            result = subprocess.run(['aws', '--version'], 
                                  capture_output=True, text=True, check=True)
            aws_version = result.stdout.strip().split()[0]
            
            # Check credentials
            result = subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                                  capture_output=True, text=True, check=True)
            caller_info = json.loads(result.stdout)
            account_id = caller_info.get('Account', 'Unknown')
            
            return True, f"AWS CLI {aws_version}, Account: {account_id}"
            
        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as e:
            return False, f"AWS setup issue: {str(e)}"
    
    def validate_sam_cli(self) -> Tuple[bool, str]:
        """Validate SAM CLI"""
        try:
            result = subprocess.run(['sam', '--version'], 
                                  capture_output=True, text=True, check=True)
            sam_version = result.stdout.strip()
            return True, f"SAM CLI: {sam_version}"
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            return False, f"SAM CLI not available: {str(e)}"
    
    def validate_yaml_syntax(self) -> Tuple[bool, str]:
        """Validate YAML files"""
        try:
            result = subprocess.run(['sam', 'validate', '--template', 'template.yaml'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, "SAM template is valid"
            else:
                return False, f"SAM template validation failed: {result.stderr.strip()}"
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback to basic YAML parsing
            try:
                import yaml
                with open('template.yaml', 'r') as f:
                    yaml.safe_load(f)
                return True, "YAML syntax is valid (basic check)"
            except Exception as e:
                return False, f"YAML validation failed: {str(e)}"
    
    def validate_cli_interface(self) -> Tuple[bool, str]:
        """Validate CLI interface works"""
        try:
            # Test CLI help
            result = subprocess.run([sys.executable, 'cli.py', '--help'], 
                                  capture_output=True, text=True, check=True)
            
            if 'Richmond AI Agent CLI' in result.stdout:
                return True, "CLI interface is functional"
            else:
                return False, "CLI help output unexpected"
                
        except subprocess.CalledProcessError as e:
            return False, f"CLI test failed: {e.stderr.strip()}"
    
    async def validate_agent_imports(self) -> Tuple[bool, str]:
        """Validate agent module can be imported"""
        try:
            # Test basic imports without full initialization
            sys.path.insert(0, '.')
            
            # Import main modules
            import agent
            import lambda_handler
            import load_sample_data
            
            # Check key classes exist
            if hasattr(agent, 'RichmondAgent') and hasattr(agent, 'RichmondAgentConfig'):
                return True, "Agent modules import successfully"
            else:
                return False, "Agent classes not found"
                
        except Exception as e:
            return False, f"Import error: {str(e)}"
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate validation report"""
        total_checks = len(self.results)
        passed_checks = sum(1 for result in self.results.values() if result[0])
        
        return {
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'success_rate': (passed_checks / total_checks * 100) if total_checks > 0 else 0,
            'results': self.results,
            'ready_for_deployment': passed_checks == total_checks
        }
    
    async def run_all_validations(self):
        """Run all validation checks"""
        print_header("Richmond AI Agent - Project Validation")
        
        validations = [
            ("File Structure", self.validate_file_structure),
            ("Python Syntax", self.validate_python_syntax),
            ("Dependencies", self.validate_dependencies),
            ("Environment Variables", self.validate_environment_variables),
            ("AWS Setup", self.validate_aws_setup),
            ("SAM CLI", self.validate_sam_cli),
            ("YAML Syntax", self.validate_yaml_syntax),
            ("CLI Interface", self.validate_cli_interface),
            ("Agent Imports", self.validate_agent_imports),
        ]
        
        for name, validation_func in validations:
            try:
                if asyncio.iscoroutinefunction(validation_func):
                    passed, details = await validation_func()
                else:
                    passed, details = validation_func()
                
                self.results[name] = (passed, details)
                print_check(name, passed, details)
                
            except Exception as e:
                self.results[name] = (False, f"Validation error: {str(e)}")
                print_check(name, False, f"Validation error: {str(e)}")
        
        # Generate and display report
        report = self.generate_report()
        self.display_report(report)
        
        return report
    
    def display_report(self, report: Dict[str, Any]):
        """Display validation report"""
        print_header("Validation Report")
        
        success_rate = report['success_rate']
        passed = report['passed_checks']
        total = report['total_checks']
        
        if success_rate == 100:
            status_color = Colors.GREEN
            status_icon = "🎉"
        elif success_rate >= 80:
            status_color = Colors.YELLOW
            status_icon = "⚠️"
        else:
            status_color = Colors.RED
            status_icon = "❌"
        
        print(f"{status_icon} {status_color}Validation Results: {passed}/{total} checks passed ({success_rate:.1f}%){Colors.END}")
        
        if report['ready_for_deployment']:
            print(f"{Colors.GREEN}{Colors.BOLD}✅ Project is ready for deployment!{Colors.END}")
            print(f"\n{Colors.CYAN}Next steps:{Colors.END}")
            print(f"   1. Run: {Colors.BOLD}python test_local.py{Colors.END}")
            print(f"   2. Deploy: {Colors.BOLD}./deploy.sh --stage dev --api-key $ANTHROPIC_API_KEY{Colors.END}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}❌ Project needs attention before deployment{Colors.END}")
            print(f"\n{Colors.CYAN}Failed checks to fix:{Colors.END}")
            
            for name, (passed, details) in report['results'].items():
                if not passed:
                    print(f"   • {Colors.RED}{name}{Colors.END}: {details}")
        
        print(f"\n{Colors.CYAN}For detailed setup help, run: {Colors.BOLD}python setup.py{Colors.END}")


async def main():
    """Main validation function"""
    validator = ProjectValidator()
    report = await validator.run_all_validations()
    
    # Exit with appropriate code
    sys.exit(0 if report['ready_for_deployment'] else 1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Validation interrupted by user{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error during validation: {e}{Colors.END}")
        sys.exit(1)