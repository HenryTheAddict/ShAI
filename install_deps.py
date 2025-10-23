#!/usr/bin/env python3
"""
ShAI Dependency Installation Script for Shared Hosting

A standalone script to install required Python packages on shared hosting
environments where standard pip installation might have issues.

Features:
- Multiple installation methods
- Shared hosting compatibility
- Progress tracking
- Clear error reporting
- No external dependencies

Usage:
    python install_deps.py
    python install_deps.py --requirements requirements.txt
    python install_deps.py --package flask
    python install_deps.py --verify-only
"""

import os
import sys
import subprocess
import argparse
import json
from pathlib import Path


class DependencyInstaller:
    """Handles dependency installation for shared hosting environments."""

    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.required_packages = [
            "flask>=2.3.0",
            "requests>=2.31.0",
            "gunicorn>=21.2.0",
            "Werkzeug>=2.3.0",
        ]

        # Common Python executables on shared hosting
        self.python_executables = [
            sys.executable,
            "python3",
            "python3.11",
            "python3.10",
            "python3.9",
            "python",
            "/usr/local/bin/python3",
            "/usr/local/bin/python3.11",
            "/usr/local/bin/python3.10",
            "/opt/alt/python311/bin/python3",
            "/opt/alt/python310/bin/python3",
            "/opt/alt/python39/bin/python3",
        ]

        # Common pip commands to try
        self.pip_commands = [
            [sys.executable, "-m", "pip"],
            ["pip3"],
            ["pip"],
            [sys.executable, "-m", "ensurepip", "--upgrade"],
        ]

    def log(self, message, level="INFO"):
        """Simple logging without Unicode characters."""
        timestamp = __import__("datetime").datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "[INFO]",
            "SUCCESS": "[OK]  ",
            "WARNING": "[WARN]",
            "ERROR": "[ERR] ",
        }.get(level, "[INFO]")

        print(f"{timestamp} {prefix} {message}")

    def find_working_python(self):
        """Find a working Python executable."""
        self.log("Detecting Python installation...")

        for python_exe in self.python_executables:
            try:
                result = subprocess.run(
                    [python_exe, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    version = result.stdout.strip()
                    self.log(f"Found Python: {python_exe} ({version})", "SUCCESS")
                    return python_exe
            except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
                continue

        self.log("Could not find working Python executable", "ERROR")
        return None

    def find_working_pip(self):
        """Find a working pip command."""
        self.log("Detecting pip installation...")

        for pip_cmd in self.pip_commands:
            try:
                result = subprocess.run(
                    pip_cmd + ["--version"], capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    version = result.stdout.strip()
                    self.log(f"Found pip: {' '.join(pip_cmd)} ({version})", "SUCCESS")
                    return pip_cmd
            except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
                continue

        self.log("Could not find working pip command", "ERROR")
        return None

    def check_package_installed(self, package_name):
        """Check if a package is already installed."""
        try:
            # Remove version specifiers for import test
            import_name = package_name.split(">=")[0].split("==")[0].split("<=")[0]
            __import__(import_name)
            return True
        except ImportError:
            return False

    def get_installed_packages(self):
        """Get list of currently installed packages."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception:
            pass

        return []

    def install_package(self, package, pip_cmd):
        """Install a single package."""
        self.log(f"Installing {package}...")

        # Try user installation first (recommended for shared hosting)
        install_cmd = pip_cmd + ["install", "--user", package]

        try:
            result = subprocess.run(
                install_cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
            )

            if result.returncode == 0:
                self.log(f"Successfully installed {package}", "SUCCESS")
                return True
            else:
                self.log(f"Failed to install {package}: {result.stderr}", "ERROR")

                # Try without --user flag
                self.log(f"Retrying {package} without --user flag...")
                install_cmd = pip_cmd + ["install", package]

                result = subprocess.run(
                    install_cmd, capture_output=True, text=True, timeout=300
                )

                if result.returncode == 0:
                    self.log(
                        f"Successfully installed {package} (system-wide)", "SUCCESS"
                    )
                    return True
                else:
                    self.log(f"Final install attempt failed for {package}", "ERROR")
                    return False

        except subprocess.TimeoutExpired:
            self.log(f"Installation timeout for {package}", "ERROR")
            return False
        except Exception as e:
            self.log(f"Installation error for {package}: {str(e)}", "ERROR")
            return False

    def install_from_requirements(self, requirements_file=None):
        """Install packages from requirements.txt."""
        if requirements_file is None:
            requirements_file = self.project_root / "requirements.txt"

        requirements_path = Path(requirements_file)

        if not requirements_path.exists():
            self.log(f"Requirements file not found: {requirements_path}", "ERROR")
            return False

        self.log(f"Reading requirements from: {requirements_path}")

        try:
            with open(requirements_path, "r") as f:
                packages = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        packages.append(line)

            if not packages:
                self.log("No packages found in requirements file", "WARNING")
                return False

            return self.install_packages(packages)

        except Exception as e:
            self.log(f"Error reading requirements file: {str(e)}", "ERROR")
            return False

    def install_packages(self, packages=None):
        """Install a list of packages."""
        if packages is None:
            packages = self.required_packages

        self.log(f"Starting installation of {len(packages)} packages...")

        # Find working pip
        pip_cmd = self.find_working_pip()
        if not pip_cmd:
            self.log("Cannot proceed without working pip command", "ERROR")
            return False

        success_count = 0
        total_packages = len(packages)

        for i, package in enumerate(packages, 1):
            self.log(f"[{i}/{total_packages}] Processing {package}")

            # Check if already installed
            package_name = package.split(">=")[0].split("==")[0].split("<=")[0]
            if self.check_package_installed(package_name):
                self.log(f"{package_name} is already installed", "SUCCESS")
                success_count += 1
                continue

            # Install the package
            if self.install_package(package, pip_cmd):
                success_count += 1

        # Summary
        self.log("=" * 50)
        self.log(
            f"Installation Summary: {success_count}/{total_packages} packages successful"
        )

        if success_count == total_packages:
            self.log("All packages installed successfully!", "SUCCESS")
            return True
        elif success_count > 0:
            self.log(
                f"Partial success: {total_packages - success_count} packages failed",
                "WARNING",
            )
            return False
        else:
            self.log("All package installations failed", "ERROR")
            return False

    def verify_installation(self):
        """Verify that all required packages are installed."""
        self.log("Verifying package installation...")

        missing_packages = []
        installed_packages = []

        for package in self.required_packages:
            package_name = package.split(">=")[0].split("==")[0].split("<=")[0]
            if self.check_package_installed(package_name):
                installed_packages.append(package_name)
                self.log(f"{package_name}: OK", "SUCCESS")
            else:
                missing_packages.append(package_name)
                self.log(f"{package_name}: MISSING", "ERROR")

        self.log("=" * 50)
        self.log(f"Verification Summary:")
        self.log(f"  Installed: {len(installed_packages)}")
        self.log(f"  Missing:   {len(missing_packages)}")

        if missing_packages:
            self.log(f"Missing packages: {', '.join(missing_packages)}", "WARNING")
            return False
        else:
            self.log("All required packages are installed!", "SUCCESS")
            return True

    def show_system_info(self):
        """Display system information for debugging."""
        self.log("System Information:")
        self.log(f"  Python Version: {sys.version}")
        self.log(f"  Python Executable: {sys.executable}")
        self.log(f"  Platform: {sys.platform}")
        self.log(f"  Project Root: {self.project_root}")

        # Show Python path
        self.log("  Python Path (first 5 entries):")
        for i, path in enumerate(sys.path[:5]):
            self.log(f"    {i + 1}. {path}")

        # Show installed packages
        installed = self.get_installed_packages()
        if installed:
            self.log(f"  Total Installed Packages: {len(installed)}")
            # Show Flask-related packages
            flask_packages = [
                pkg for pkg in installed if "flask" in pkg["name"].lower()
            ]
            if flask_packages:
                self.log("  Flask-related packages:")
                for pkg in flask_packages:
                    self.log(f"    - {pkg['name']} ({pkg['version']})")

    def create_manual_instructions(self):
        """Create manual installation instructions."""
        instructions_file = self.project_root / "MANUAL_INSTALL.txt"

        instructions = f"""ShAI Manual Installation Instructions
{"=" * 40}

If the automatic installation script fails, try these manual methods:

Method 1: SSH/Terminal Installation
----------------------------------
If you have SSH access to your hosting account:

1. Connect via SSH
2. Navigate to your project directory:
   cd {self.project_root}

3. Try these commands (in order):
   {sys.executable} -m pip install --user flask requests gunicorn Werkzeug

   OR

   pip3 install --user flask requests gunicorn Werkzeug

   OR

   python3 -m pip install --user flask requests gunicorn Werkzeug

Method 2: cPanel Python Selector
--------------------------------
If your hosting provider has cPanel with Python Selector:

1. Go to cPanel → Software → Python Selector
2. Select your Python version
3. Click "Manage" for your application
4. Go to "Packages" section
5. Install these packages:
   - flask
   - requests
   - gunicorn
   - Werkzeug

Method 3: Upload and Install
---------------------------
1. Upload requirements.txt to your hosting account
2. In hosting control panel, find Python package manager
3. Use "Install from requirements.txt" option

Method 4: Contact Hosting Support
---------------------------------
If all methods fail, contact your hosting provider support with this information:

- You need Python packages installed
- Package names: flask, requests, gunicorn, Werkzeug
- You're running a Python web application
- Provide this file as reference

Requirements File Content:
{"-" * 25}
"""

        # Add requirements content
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            with open(requirements_file, "r") as f:
                instructions += f.read()
        else:
            for package in self.required_packages:
                instructions += f"{package}\n"

        try:
            with open(instructions_file, "w") as f:
                f.write(instructions)
            self.log(f"Created manual instructions: {instructions_file}", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"Failed to create instructions file: {str(e)}", "ERROR")
            return False


def main():
    """Main function with command line arguments."""
    parser = argparse.ArgumentParser(
        description="ShAI Dependency Installation Script for Shared Hosting"
    )
    parser.add_argument("--requirements", help="Path to requirements.txt file")
    parser.add_argument("--package", help="Install a specific package")
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify installation, don't install",
    )
    parser.add_argument(
        "--info", action="store_true", help="Show system information only"
    )
    parser.add_argument(
        "--manual", action="store_true", help="Create manual installation instructions"
    )

    args = parser.parse_args()

    installer = DependencyInstaller()

    # Show header
    print("=" * 60)
    print("ShAI Dependency Installation Script")
    print("=" * 60)

    if args.info:
        installer.show_system_info()
        return

    if args.manual:
        installer.create_manual_instructions()
        return

    if args.verify_only:
        success = installer.verify_installation()
        sys.exit(0 if success else 1)

    # Show system info first
    installer.show_system_info()
    print()

    # Install packages
    if args.package:
        success = installer.install_packages([args.package])
    elif args.requirements:
        success = installer.install_from_requirements(args.requirements)
    else:
        # Install default required packages
        success = installer.install_packages()

    # Verify installation
    print()
    verification_success = installer.verify_installation()

    # Create manual instructions if installation failed
    if not success or not verification_success:
        print()
        installer.log("Creating manual installation instructions...", "INFO")
        installer.create_manual_instructions()

    final_success = success and verification_success

    print()
    print("=" * 60)
    if final_success:
        installer.log("Installation completed successfully!", "SUCCESS")
        installer.log("You can now run your ShAI application.", "INFO")
    else:
        installer.log("Installation completed with issues.", "WARNING")
        installer.log("Check MANUAL_INSTALL.txt for alternative methods.", "INFO")
    print("=" * 60)

    sys.exit(0 if final_success else 1)


if __name__ == "__main__":
    main()
