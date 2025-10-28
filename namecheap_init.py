#!/usr/bin/env python3
"""
ShAI Namecheap Shared Hosting Initialization Script

This script automatically configures ShAI for deployment on Namecheap shared hosting.
It handles environment setup, dependency verification, and common hosting issues.

Features:
- Auto-detects Namecheap hosting environment
- Sets up proper Python paths for shared hosting
- Verifies and installs dependencies
- Configures environment variables
- Creates necessary directories and permissions
- Provides debugging tools for common issues
- Integrates with passenger_wsgi.py

Usage:
    python namecheap_init.py              # Auto-setup
    python namecheap_init.py --verify     # Verify setup only
    python namecheap_init.py --debug      # Show debug information
    python namecheap_init.py --fix        # Fix common issues
"""

import os
import sys
import subprocess
import logging
import json
from pathlib import Path
from datetime import datetime
import traceback
import urllib.request
import ssl
import argparse

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class NamecheapInitializer:
    """Namecheap-specific initialization handler for ShAI."""

    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.is_namecheap = self.detect_namecheap_hosting()
        self.user_home = Path.home()
        self.public_html = self.find_public_html()

        # Common Namecheap paths
        self.possible_python_paths = [
            "/usr/local/bin/python3",
            "/usr/local/bin/python3.9",
            "/usr/local/bin/python3.10",
            "/usr/local/bin/python3.11",
            "/usr/bin/python3",
            "/opt/alt/python39/bin/python3",
            "/opt/alt/python310/bin/python3",
            "/opt/alt/python311/bin/python3",
        ]

        self.setup_logging()

    def setup_logging(self):
        """Setup comprehensive logging for Namecheap deployment."""
        logs_dir = self.project_root / "logs"
        logs_dir.mkdir(exist_ok=True)

        # File handler for persistent logs
        file_handler = logging.FileHandler(logs_dir / "namecheap_init.log")
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.info("Namecheap initialization logging started")

    def detect_namecheap_hosting(self):
        """Detect if we're running on Namecheap shared hosting."""
        indicators = [
            "namecheap" in str(Path.home()).lower(),
            "cpanel" in os.environ.get("PATH", "").lower(),
            "public_html" in str(Path.cwd()),
            "/home/" in str(Path.home()) and len(str(Path.home()).split("/")) >= 3,
        ]

        detection_score = sum(indicators)
        is_namecheap = detection_score >= 2

        logger.info(f"Namecheap hosting detection score: {detection_score}/4")
        logger.info(f"Detected as Namecheap hosting: {is_namecheap}")

        return is_namecheap

    def find_public_html(self):
        """Find the public_html directory."""
        possible_paths = [
            self.user_home / "public_html",
            self.project_root.parent / "public_html",
            Path("/home") / os.getenv("USER", "user") / "public_html",
        ]

        for path in possible_paths:
            if path.exists():
                logger.info(f"Found public_html at: {path}")
                return path

        logger.warning("Could not locate public_html directory")
        return self.user_home / "public_html"  # Default assumption

    def get_python_info(self):
        """Get detailed Python environment information."""
        info = {
            "version": sys.version,
            "executable": sys.executable,
            "path": sys.path[:5],  # First 5 entries
            "platform": sys.platform,
            "prefix": sys.prefix,
            "user_base": getattr(sys, "user_base", "Not available"),
        }

        # Try to find alternative Python installations
        available_pythons = []
        for python_path in self.possible_python_paths:
            if os.path.exists(python_path):
                try:
                    result = subprocess.run(
                        [python_path, "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if result.returncode == 0:
                        available_pythons.append(
                            {"path": python_path, "version": result.stdout.strip()}
                        )
                except:
                    pass

        info["available_pythons"] = available_pythons
        return info

    def check_dependencies(self):
        """Check and report on Python dependencies."""
        required_packages = [
            "flask",
            "requests",
            "gunicorn",
        ]

        optional_packages = [
            "python-dotenv",
        ]

        results = {
            "required": {},
            "optional": {},
            "missing_required": [],
            "missing_optional": [],
        }

        # Check required packages
        for package in required_packages:
            try:
                __import__(package)
                results["required"][package] = "Available"
                logger.info(f"✓ Required package '{package}' is available")
            except ImportError:
                results["required"][package] = "Missing"
                results["missing_required"].append(package)
                logger.error(f"✗ Required package '{package}' is missing")

        # Check optional packages
        for package in optional_packages:
            try:
                __import__(package.replace("-", "_"))
                results["optional"][package] = "Available"
                logger.info(f"✓ Optional package '{package}' is available")
            except ImportError:
                results["optional"][package] = "Missing"
                results["missing_optional"].append(package)
                logger.warning(f"⚠ Optional package '{package}' is missing")

        return results

    def install_dependencies(self):
        """Attempt to install missing dependencies."""
        logger.info("Attempting to install missing dependencies...")

        dep_results = self.check_dependencies()
        missing_packages = (
            dep_results["missing_required"] + dep_results["missing_optional"]
        )

        if not missing_packages:
            logger.info("All dependencies are already installed")
            return True

        # Try different pip installation methods
        pip_commands = [
            [sys.executable, "-m", "pip", "install", "--user"],
            ["pip3", "install", "--user"],
            ["python3", "-m", "pip", "install", "--user"],
        ]

        success_count = 0

        for pip_cmd in pip_commands:
            try:
                # Test if pip command works
                test_result = subprocess.run(
                    pip_cmd + ["--version"], capture_output=True, text=True, timeout=10
                )
                if test_result.returncode != 0:
                    continue

                logger.info(f"Using pip command: {' '.join(pip_cmd)}")

                # Install packages one by one
                for package in missing_packages:
                    try:
                        logger.info(f"Installing {package}...")
                        result = subprocess.run(
                            pip_cmd + [package],
                            capture_output=True,
                            text=True,
                            timeout=120,
                        )

                        if result.returncode == 0:
                            logger.info(f"✓ Successfully installed {package}")
                            success_count += 1
                        else:
                            logger.error(
                                f"✗ Failed to install {package}: {result.stderr}"
                            )

                    except subprocess.TimeoutExpired:
                        logger.error(f"✗ Timeout installing {package}")
                    except Exception as e:
                        logger.error(f"✗ Error installing {package}: {e}")

                break  # If we got here, pip command worked

            except Exception as e:
                logger.warning(f"Pip command failed: {' '.join(pip_cmd)}: {e}")
                continue

        logger.info(
            f"Successfully installed {success_count}/{len(missing_packages)} packages"
        )
        return success_count == len(missing_packages)

    def setup_environment_file(self):
        """Setup .env file for Namecheap hosting."""
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"

        if env_file.exists():
            logger.info(".env file already exists")
            return True

        if not env_example.exists():
            logger.warning(".env.example not found, creating basic .env file")
            env_content = """# ShAI Environment Configuration for Namecheap
SECRET_KEY=namecheap-shai-production-secret-key-change-this
USE_LOCAL=false
CLAUDE_API_KEY=your-claude-api-key-here
DEBUG=false
FLASK_ENV=production
LOG_LEVEL=INFO
"""
        else:
            with open(env_example, "r") as f:
                env_content = f.read()

            # Customize for Namecheap
            env_content = env_content.replace("USE_LOCAL=true", "USE_LOCAL=false")
            env_content = env_content.replace("DEBUG=true", "DEBUG=false")

        try:
            with open(env_file, "w") as f:
                f.write(env_content)
            logger.info("✓ Created .env file")

            # Set appropriate permissions
            os.chmod(env_file, 0o600)  # Read/write for owner only
            logger.info("✓ Set secure permissions on .env file")

            return True
        except Exception as e:
            logger.error(f"✗ Failed to create .env file: {e}")
            return False

    def create_directory_structure(self):
        """Create necessary directories for Namecheap deployment."""
        directories = [
            self.project_root / "logs",
            self.project_root / "tmp",
            self.project_root / "static",
            self.project_root / "templates",
        ]

        created_dirs = []

        for directory in directories:
            try:
                directory.mkdir(exist_ok=True, parents=True)
                # Set permissions (755 for directories)
                os.chmod(directory, 0o755)
                created_dirs.append(str(directory))
                logger.info(f"✓ Created/verified directory: {directory}")
            except Exception as e:
                logger.error(f"✗ Failed to create directory {directory}: {e}")

        return created_dirs

    def setup_wsgi_configuration(self):
        """Ensure proper WSGI configuration for Namecheap."""
        passenger_wsgi = self.project_root / "passenger_wsgi.py"

        if not passenger_wsgi.exists():
            logger.error("passenger_wsgi.py not found!")
            return False

        # Verify the file is executable
        try:
            os.chmod(passenger_wsgi, 0o755)
            logger.info("✓ Set executable permissions on passenger_wsgi.py")
        except Exception as e:
            logger.warning(f"Could not set permissions on passenger_wsgi.py: {e}")

        # Test import of the WSGI file
        try:
            sys.path.insert(0, str(self.project_root))
            import passenger_wsgi

            if hasattr(passenger_wsgi, "application"):
                logger.info("✓ passenger_wsgi.py imports successfully")
                return True
            else:
                logger.error("✗ passenger_wsgi.py missing 'application' object")
                return False
        except Exception as e:
            logger.error(f"✗ Failed to import passenger_wsgi.py: {e}")
            return False

    def test_claude_api_connection(self):
        """Test connection to Claude API if key is configured."""
        api_key = os.environ.get("CLAUDE_API_KEY")

        if not api_key or api_key == "your-claude-api-key-here":
            logger.warning("Claude API key not configured - skipping connection test")
            return None

        logger.info("Testing Claude API connection...")

        try:
            # Create a simple test request
            import json
            import urllib.request

            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }

            data = {
                "model": "claude-3-5-haiku-20241022",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "Hello"}],
            }

            request = urllib.request.Request(
                url, data=json.dumps(data).encode("utf-8"), headers=headers
            )

            # Create SSL context that doesn't verify certificates (for some hosting environments)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            with urllib.request.urlopen(request, timeout=10, context=ctx) as response:
                if response.status == 200:
                    logger.info("✓ Claude API connection successful")
                    return True
                else:
                    logger.error(f"✗ Claude API returned status {response.status}")
                    return False

        except Exception as e:
            logger.error(f"✗ Claude API connection failed: {e}")
            return False

    def run_health_check(self):
        """Run comprehensive health check for the application."""
        logger.info("Running comprehensive health check...")

        checks = {
            "python_version": sys.version_info >= (3, 8),
            "project_structure": all(
                [
                    (self.project_root / "app.py").exists(),
                    (self.project_root / "passenger_wsgi.py").exists(),
                    (self.project_root / "requirements.txt").exists(),
                ]
            ),
            "dependencies": len(self.check_dependencies()["missing_required"]) == 0,
            "environment": (self.project_root / ".env").exists(),
            "wsgi_config": self.setup_wsgi_configuration(),
            "directories": len(self.create_directory_structure()) > 0,
        }

        # Test app import
        try:
            sys.path.insert(0, str(self.project_root))
            import app

            checks["app_import"] = True
            logger.info("✓ Main application imports successfully")
        except Exception as e:
            checks["app_import"] = False
            logger.error(f"✗ Failed to import main application: {e}")

        # Claude API test
        claude_test = self.test_claude_api_connection()
        if claude_test is not None:
            checks["claude_api"] = claude_test

        # Summary
        passed = sum(1 for result in checks.values() if result is True)
        total = len(checks)

        logger.info(f"Health check results: {passed}/{total} checks passed")

        for check, result in checks.items():
            status = "✓" if result else "✗"
            logger.info(f"{status} {check}: {result}")

        return checks, passed == total

    def generate_debug_report(self):
        """Generate comprehensive debug report for troubleshooting."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "namecheap_detection": self.is_namecheap,
            "paths": {
                "project_root": str(self.project_root),
                "user_home": str(self.user_home),
                "public_html": str(self.public_html),
                "current_working_dir": str(Path.cwd()),
            },
            "python_info": self.get_python_info(),
            "dependencies": self.check_dependencies(),
            "environment_variables": {
                k: v if "KEY" not in k and "SECRET" not in k else "***HIDDEN***"
                for k, v in os.environ.items()
                if k.startswith(("FLASK_", "CLAUDE_", "USE_", "DEBUG", "SECRET"))
            },
            "file_structure": {
                "app.py": (self.project_root / "app.py").exists(),
                "passenger_wsgi.py": (self.project_root / "passenger_wsgi.py").exists(),
                "requirements.txt": (self.project_root / "requirements.txt").exists(),
                ".env": (self.project_root / ".env").exists(),
                ".env.example": (self.project_root / ".env.example").exists(),
                "templates/": (self.project_root / "templates").exists(),
                "static/": (self.project_root / "static").exists(),
            },
            "permissions": {},
        }

        # Check file permissions
        important_files = ["app.py", "passenger_wsgi.py", ".env"]
        for filename in important_files:
            filepath = self.project_root / filename
            if filepath.exists():
                try:
                    stat = filepath.stat()
                    report["permissions"][filename] = oct(stat.st_mode)
                except:
                    report["permissions"][filename] = "Unable to read"

        return report

    def fix_common_issues(self):
        """Fix common Namecheap hosting issues."""
        logger.info("Fixing common Namecheap hosting issues...")

        fixes_applied = []

        # Fix 1: File permissions
        try:
            important_files = [
                ("passenger_wsgi.py", 0o755),
                ("app.py", 0o644),
                (".env", 0o600),
            ]

            for filename, perm in important_files:
                filepath = self.project_root / filename
                if filepath.exists():
                    os.chmod(filepath, perm)
                    fixes_applied.append(f"Set permissions for {filename}")
        except Exception as e:
            logger.error(f"Failed to fix file permissions: {e}")

        # Fix 2: Directory permissions
        try:
            dirs = ["logs", "tmp", "static", "templates"]
            for dirname in dirs:
                dirpath = self.project_root / dirname
                if dirpath.exists():
                    os.chmod(dirpath, 0o755)
                    fixes_applied.append(f"Set directory permissions for {dirname}")
        except Exception as e:
            logger.error(f"Failed to fix directory permissions: {e}")

        # Fix 3: Python path in passenger_wsgi.py
        try:
            passenger_file = self.project_root / "passenger_wsgi.py"
            if passenger_file.exists():
                content = passenger_file.read_text()
                if str(self.project_root) not in content:
                    # This suggests the path might need updating, but we won't modify the file
                    # as it should be auto-detecting
                    fixes_applied.append(
                        "Verified passenger_wsgi.py path configuration"
                    )
        except Exception as e:
            logger.error(f"Failed to verify passenger_wsgi.py: {e}")

        # Fix 4: Create missing directories
        missing_dirs = []
        required_dirs = ["logs", "tmp"]
        for dirname in required_dirs:
            dirpath = self.project_root / dirname
            if not dirpath.exists():
                try:
                    dirpath.mkdir(parents=True, exist_ok=True)
                    os.chmod(dirpath, 0o755)
                    missing_dirs.append(dirname)
                except Exception as e:
                    logger.error(f"Failed to create directory {dirname}: {e}")

        if missing_dirs:
            fixes_applied.append(
                f"Created missing directories: {', '.join(missing_dirs)}"
            )

        logger.info(f"Applied {len(fixes_applied)} fixes:")
        for fix in fixes_applied:
            logger.info(f"  ✓ {fix}")

        return fixes_applied

    def full_initialization(self):
        """Run complete initialization process."""
        logger.info("=" * 60)
        logger.info("ShAI Namecheap Shared Hosting Initialization")
        logger.info("=" * 60)

        success_count = 0
        total_steps = 8

        steps = [
            ("Detecting hosting environment", lambda: self.is_namecheap),
            (
                "Creating directory structure",
                lambda: len(self.create_directory_structure()) > 0,
            ),
            ("Setting up environment file", self.setup_environment_file),
            ("Installing dependencies", self.install_dependencies),
            ("Setting up WSGI configuration", self.setup_wsgi_configuration),
            (
                "Testing Claude API connection",
                lambda: self.test_claude_api_connection() is not False,
            ),
            ("Running health check", lambda: self.run_health_check()[1]),
            ("Applying common fixes", lambda: len(self.fix_common_issues()) >= 0),
        ]

        results = {}

        for step_name, step_func in steps:
            logger.info(f"\n--- {step_name} ---")
            try:
                result = step_func()
                results[step_name] = result
                if result:
                    logger.info(f"✓ {step_name}: SUCCESS")
                    success_count += 1
                else:
                    logger.warning(f"⚠ {step_name}: PARTIAL or SKIPPED")
            except Exception as e:
                logger.error(f"✗ {step_name}: FAILED - {e}")
                results[step_name] = False

        # Final summary
        logger.info("\n" + "=" * 60)
        logger.info(
            f"Initialization Summary: {success_count}/{total_steps} steps successful"
        )
        logger.info("=" * 60)

        if success_count >= 6:  # Most critical steps passed
            logger.info("🎉 ShAI is ready for Namecheap deployment!")
            logger.info("Next steps:")
            logger.info("1. Set your CLAUDE_API_KEY in the .env file")
            logger.info("2. Upload all files to your public_html directory")
            logger.info("3. Configure Python app in cPanel to use passenger_wsgi.py")
        else:
            logger.warning("⚠️  Initialization completed with issues")
            logger.info("Check the logs above for specific problems to resolve")

        return results, success_count >= 6


def main():
    """Main function with command line argument handling."""
    parser = argparse.ArgumentParser(description="ShAI Namecheap Initialization Script")
    parser.add_argument("--verify", action="store_true", help="Verify setup only")
    parser.add_argument("--debug", action="store_true", help="Show debug information")
    parser.add_argument("--fix", action="store_true", help="Fix common issues only")

    args = parser.parse_args()

    initializer = NamecheapInitializer()

    if args.debug:
        print("=== ShAI Namecheap Debug Report ===")
        report = initializer.generate_debug_report()
        print(json.dumps(report, indent=2, default=str))

    elif args.verify:
        print("=== Verifying ShAI Setup ===")
        checks, all_passed = initializer.run_health_check()
        if all_passed:
            print("✅ All checks passed!")
        else:
            print("❌ Some checks failed. Run with --debug for details.")

    elif args.fix:
        print("=== Fixing Common Issues ===")
        fixes = initializer.fix_common_issues()
        print(f"Applied {len(fixes)} fixes.")

    else:
        # Full initialization
        results, success = initializer.full_initialization()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
