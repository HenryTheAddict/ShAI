#!/usr/bin/env python3
"""
ShAI Deployment Script

Automates the setup and deployment process for ShAI application.
Supports both local development and production deployment.

Usage:
    python deploy.py --local          # Setup for local development
    python deploy.py --production     # Setup for production
    python deploy.py --check          # Check current setup
    python deploy.py --help           # Show help
"""

import os
import sys
import subprocess
import json
import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Optional


class ShAIDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.env_file = self.project_root / ".env"
        self.requirements_file = self.project_root / "requirements.txt"

    def log(self, message: str, level: str = "INFO"):
        """Simple logging function"""
        colors = {
            "INFO": "\033[94m",  # Blue
            "SUCCESS": "\033[92m",  # Green
            "WARNING": "\033[93m",  # Yellow
            "ERROR": "\033[91m",  # Red
            "RESET": "\033[0m",  # Reset
        }

        color = colors.get(level, colors["INFO"])
        reset = colors["RESET"]
        print(f"{color}[{level}]{reset} {message}")

    def run_command(
        self, command: List[str], check: bool = True
    ) -> Optional[subprocess.CompletedProcess]:
        """Run a shell command safely"""
        try:
            self.log(f"Running: {' '.join(command)}")
            result = subprocess.run(
                command, capture_output=True, text=True, check=check
            )
            if result.stdout:
                print(result.stdout.strip())
            return result
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {e}", "ERROR")
            if e.stderr:
                self.log(f"Error output: {e.stderr}", "ERROR")
            return None
        except FileNotFoundError:
            self.log(f"Command not found: {command[0]}", "ERROR")
            return None

    def check_python_version(self) -> bool:
        """Check if Python version is compatible"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.log(
                f"Python {version.major}.{version.minor} is too old. Need Python 3.8+",
                "ERROR",
            )
            return False

        self.log(
            f"Python {version.major}.{version.minor}.{version.micro} is compatible",
            "SUCCESS",
        )
        return True

    def setup_virtual_environment(self) -> bool:
        """Create and setup virtual environment"""
        venv_path = self.project_root / "venv"

        if venv_path.exists():
            self.log("Virtual environment already exists", "INFO")
            return True

        self.log("Creating virtual environment...", "INFO")
        result = self.run_command([sys.executable, "-m", "venv", str(venv_path)])
        if result is None:
            return False

        self.log("Virtual environment created successfully", "SUCCESS")
        return True

    def install_dependencies(self) -> bool:
        """Install Python dependencies"""
        if not self.requirements_file.exists():
            self.log("requirements.txt not found", "ERROR")
            return False

        # Determine pip path
        venv_path = self.project_root / "venv"
        if venv_path.exists():
            if os.name == "nt":  # Windows
                pip_path = venv_path / "Scripts" / "pip"
            else:  # Unix-like
                pip_path = venv_path / "bin" / "pip"
        else:
            pip_path = "pip"

        self.log("Installing dependencies...", "INFO")
        result = self.run_command(
            [str(pip_path), "install", "-r", str(self.requirements_file)]
        )

        if result is None:
            # Fallback to system pip
            result = self.run_command(
                ["pip", "install", "-r", str(self.requirements_file)]
            )

        if result is not None:
            self.log("Dependencies installed successfully", "SUCCESS")
            return True
        else:
            self.log("Failed to install dependencies", "ERROR")
            return False

    def setup_environment_file(self, config_type: str) -> bool:
        """Setup environment file based on deployment type"""
        env_example = self.project_root / ".env.example"

        if not env_example.exists():
            self.log(".env.example file not found", "ERROR")
            return False

        # Read example file
        with open(env_example, "r") as f:
            env_content = f.read()

        # Configure for different deployment types
        if config_type == "local":
            env_content = env_content.replace("USE_LOCAL=false", "USE_LOCAL=true")
            env_content = env_content.replace("DEBUG=false", "DEBUG=true")
            env_content = env_content.replace(
                "your-secret-key-here-change-this-in-production", "dev-secret-key-local"
            )
        elif config_type == "production":
            env_content = env_content.replace("USE_LOCAL=true", "USE_LOCAL=false")
            env_content = env_content.replace("DEBUG=true", "DEBUG=false")
            self.log("Remember to set your CLAUDE_API_KEY in .env file!", "WARNING")

        # Write environment file
        with open(self.env_file, "w") as f:
            f.write(env_content)

        self.log(f"Environment file created for {config_type} deployment", "SUCCESS")
        return True

    def check_ollama_installation(self) -> bool:
        """Check if Ollama is installed and running"""
        self.log("Checking Ollama installation...", "INFO")

        # Check if ollama command exists
        result = self.run_command(["ollama", "version"], check=False)
        if result is None or result.returncode != 0:
            self.log("Ollama is not installed", "WARNING")
            self.log("Install from: https://ollama.ai/", "INFO")
            return False

        # Check if Ollama service is running
        try:
            import requests

            response = requests.get("http://localhost:11434", timeout=5)
            if response.status_code == 200:
                self.log("Ollama is running", "SUCCESS")
                return True
            else:
                self.log("Ollama is installed but not running", "WARNING")
                self.log("Start with: ollama serve", "INFO")
                return False
        except Exception:
            self.log("Ollama is installed but not running", "WARNING")
            self.log("Start with: ollama serve", "INFO")
            return False

    def setup_ollama_model(self) -> bool:
        """Download and setup a model for Ollama"""
        if not self.check_ollama_installation():
            return False

        self.log("Checking for Ollama models...", "INFO")
        result = self.run_command(["ollama", "list"], check=False)

        if result and "llama2" in result.stdout:
            self.log("llama2 model is already installed", "SUCCESS")
            return True

        self.log("Downloading llama2 model (this may take a while)...", "INFO")
        result = self.run_command(["ollama", "pull", "llama2"])

        if result is not None:
            self.log("llama2 model installed successfully", "SUCCESS")
            return True
        else:
            self.log("Failed to install llama2 model", "ERROR")
            return False

    def validate_configuration(self) -> bool:
        """Validate the current configuration"""
        self.log("Validating configuration...", "INFO")

        if not self.env_file.exists():
            self.log(".env file not found", "ERROR")
            return False

        # Load environment variables
        env_vars = {}
        with open(self.env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key] = value

        # Check required variables
        required_vars = ["SECRET_KEY", "USE_LOCAL"]
        missing_vars = []

        for var in required_vars:
            if var not in env_vars or not env_vars[var]:
                missing_vars.append(var)

        if missing_vars:
            self.log(f"Missing required environment variables: {missing_vars}", "ERROR")
            return False

        # Check specific configurations
        use_local = env_vars.get("USE_LOCAL", "false").lower() == "true"

        if use_local:
            if not self.check_ollama_installation():
                self.log("Local deployment requires Ollama", "ERROR")
                return False
        else:
            if (
                not env_vars.get("CLAUDE_API_KEY")
                or env_vars.get("CLAUDE_API_KEY") == "your-claude-api-key-here"
            ):
                self.log("Production deployment requires CLAUDE_API_KEY", "ERROR")
                return False

        self.log("Configuration is valid", "SUCCESS")
        return True

    def test_application(self) -> bool:
        """Test if the application can start"""
        self.log("Testing application startup...", "INFO")

        try:
            # Try to import the app
            import sys

            sys.path.insert(0, str(self.project_root))

            from app import app

            # Try to create the app context
            with app.app_context():
                self.log("Application can start successfully", "SUCCESS")
                return True

        except Exception as e:
            self.log(f"Application startup failed: {e}", "ERROR")
            return False

    def deploy_local(self) -> bool:
        """Deploy for local development"""
        self.log("Setting up ShAI for local development...", "INFO")

        steps = [
            ("Checking Python version", self.check_python_version),
            ("Setting up virtual environment", self.setup_virtual_environment),
            ("Installing dependencies", self.install_dependencies),
            (
                "Setting up environment file",
                lambda: self.setup_environment_file("local"),
            ),
            ("Checking Ollama", self.check_ollama_installation),
            ("Setting up Ollama model", self.setup_ollama_model),
            ("Validating configuration", self.validate_configuration),
            ("Testing application", self.test_application),
        ]

        success = True
        for step_name, step_func in steps:
            self.log(f"Step: {step_name}", "INFO")
            if not step_func():
                self.log(f"Failed: {step_name}", "ERROR")
                success = False
                break

        if success:
            self.log("Local deployment setup completed successfully!", "SUCCESS")
            self.log("To start the application:", "INFO")
            self.log("1. Start Ollama: ollama serve", "INFO")
            self.log("2. Run the app: python app.py", "INFO")
            self.log("3. Visit: http://localhost:5000", "INFO")

        return success

    def deploy_production(self) -> bool:
        """Deploy for production"""
        self.log("Setting up ShAI for production deployment...", "INFO")

        steps = [
            ("Checking Python version", self.check_python_version),
            ("Installing dependencies", self.install_dependencies),
            (
                "Setting up environment file",
                lambda: self.setup_environment_file("production"),
            ),
            ("Validating configuration", self.validate_configuration),
            ("Testing application", self.test_application),
        ]

        success = True
        for step_name, step_func in steps:
            self.log(f"Step: {step_name}", "INFO")
            if not step_func():
                self.log(f"Failed: {step_name}", "ERROR")
                success = False
                break

        if success:
            self.log("Production deployment setup completed!", "SUCCESS")
            self.log("Next steps:", "INFO")
            self.log("1. Set your CLAUDE_API_KEY in the .env file", "WARNING")
            self.log("2. Upload files to your hosting provider", "INFO")
            self.log("3. Configure your web server to use passenger_wsgi.py", "INFO")
        else:
            self.log("Don't forget to set CLAUDE_API_KEY in .env!", "WARNING")

        return success

    def check_setup(self) -> bool:
        """Check current setup status"""
        self.log("Checking ShAI setup status...", "INFO")

        checks = [
            ("Python version", self.check_python_version),
            ("Environment file", lambda: self.env_file.exists()),
            ("Dependencies", lambda: self.requirements_file.exists()),
            ("Configuration", self.validate_configuration),
            ("Application", self.test_application),
        ]

        all_good = True
        for check_name, check_func in checks:
            try:
                if check_func():
                    self.log(f"✓ {check_name}", "SUCCESS")
                else:
                    self.log(f"✗ {check_name}", "ERROR")
                    all_good = False
            except Exception as e:
                self.log(f"✗ {check_name}: {e}", "ERROR")
                all_good = False

        if all_good:
            self.log("All checks passed! ShAI is ready to run.", "SUCCESS")
        else:
            self.log(
                "Some checks failed. Run deployment script to fix issues.", "WARNING"
            )

        return all_good


def main():
    parser = argparse.ArgumentParser(description="ShAI Deployment Script")
    parser.add_argument(
        "--local", action="store_true", help="Setup for local development"
    )
    parser.add_argument(
        "--production", action="store_true", help="Setup for production"
    )
    parser.add_argument("--check", action="store_true", help="Check current setup")

    args = parser.parse_args()

    deployer = ShAIDeployer()

    if args.local:
        success = deployer.deploy_local()
    elif args.production:
        success = deployer.deploy_production()
    elif args.check:
        success = deployer.check_setup()
    else:
        parser.print_help()
        return

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
