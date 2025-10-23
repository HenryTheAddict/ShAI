#!/usr/bin/env python3
"""
ShAI Quick Start Script

A simple script to launch ShAI application with minimal setup.
Automatically detects your configuration and starts the appropriate services.

Usage:
    python start.py              # Auto-detect and start
    python start.py --local      # Force local mode
    python start.py --production # Force production mode
    python start.py --help       # Show help
"""

import os
import sys
import time
import subprocess
import argparse
import webbrowser
from pathlib import Path
import signal
import threading


class ShAIStarter:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.env_file = self.project_root / ".env"
        self.ollama_process = None
        self.flask_process = None

    def log(self, message: str, level: str = "INFO"):
        """Simple colored logging"""
        colors = {
            "INFO": "\033[94m",  # Blue
            "SUCCESS": "\033[92m",  # Green
            "WARNING": "\033[93m",  # Yellow
            "ERROR": "\033[91m",  # Red
            "RESET": "\033[0m",  # Reset
        }

        color = colors.get(level, colors["INFO"])
        reset = colors["RESET"]
        timestamp = time.strftime("%H:%M:%S")
        print(f"{color}[{timestamp}]{reset} {message}")

    def check_environment(self):
        """Check if environment is properly configured"""
        if not self.env_file.exists():
            self.log("No .env file found. Running setup...", "WARNING")
            self.run_setup()
            return self.check_environment()  # Recheck after setup

        # Read environment variables
        env_vars = {}
        with open(self.env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key] = value

        use_local = env_vars.get("USE_LOCAL", "false").lower() == "true"

        if use_local:
            self.log("Configured for local development with Ollama", "INFO")
            return "local"
        else:
            claude_key = env_vars.get("CLAUDE_API_KEY", "")
            if not claude_key or claude_key == "your-claude-api-key-here":
                self.log(
                    "Production mode requires CLAUDE_API_KEY in .env file", "ERROR"
                )
                self.log(
                    "Get your API key from: https://console.anthropic.com/", "INFO"
                )
                return None
            self.log("Configured for production with Claude API", "INFO")
            return "production"

    def run_setup(self):
        """Run the deployment script to setup the environment"""
        self.log("Setting up ShAI environment...", "INFO")

        # Try to determine if user wants local or production
        choice = (
            input("Setup for [L]ocal development or [P]roduction? (L/p): ")
            .strip()
            .lower()
        )

        if choice.startswith("p"):
            setup_type = "production"
        else:
            setup_type = "local"

        try:
            result = subprocess.run(
                [sys.executable, "deploy.py", f"--{setup_type}"],
                cwd=self.project_root,
                check=True,
            )

            self.log(f"Setup completed for {setup_type} mode", "SUCCESS")

        except subprocess.CalledProcessError:
            self.log(
                "Setup failed. Please run manually: python deploy.py --help", "ERROR"
            )
            sys.exit(1)
        except FileNotFoundError:
            self.log(
                "deploy.py not found. Please ensure all files are present.", "ERROR"
            )
            sys.exit(1)

    def check_ollama(self):
        """Check if Ollama is available and start if needed"""
        try:
            # Check if Ollama is already running
            import requests

            response = requests.get("http://localhost:11434", timeout=3)
            if response.status_code == 200:
                self.log("Ollama is already running", "SUCCESS")
                return True
        except:
            pass

        # Try to start Ollama
        self.log("Starting Ollama service...", "INFO")
        try:
            # Start Ollama in background
            self.ollama_process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # Wait for Ollama to start
            for i in range(10):
                time.sleep(2)
                try:
                    import requests

                    response = requests.get("http://localhost:11434", timeout=1)
                    if response.status_code == 200:
                        self.log("Ollama started successfully", "SUCCESS")
                        return True
                except:
                    continue

            self.log("Ollama failed to start within 20 seconds", "ERROR")
            return False

        except FileNotFoundError:
            self.log("Ollama not found. Install from: https://ollama.ai/", "ERROR")
            return False
        except Exception as e:
            self.log(f"Failed to start Ollama: {e}", "ERROR")
            return False

    def check_ollama_model(self):
        """Ensure at least one model is available"""
        try:
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0 and len(result.stdout.strip().split("\n")) > 1:
                self.log("Ollama models are available", "SUCCESS")
                return True
            else:
                self.log("No Ollama models found. Downloading llama2...", "WARNING")
                self.log("This may take several minutes...", "INFO")

                download_result = subprocess.run(
                    ["ollama", "pull", "llama2"],
                    timeout=600,  # 10 minutes timeout
                )

                if download_result.returncode == 0:
                    self.log("Model downloaded successfully", "SUCCESS")
                    return True
                else:
                    self.log("Failed to download model", "ERROR")
                    return False

        except subprocess.TimeoutExpired:
            self.log("Model download timed out. Try again later.", "ERROR")
            return False
        except Exception as e:
            self.log(f"Error checking models: {e}", "ERROR")
            return False

    def start_flask_app(self, mode):
        """Start the Flask application"""
        self.log("Starting ShAI application...", "INFO")

        # Set environment variables
        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.project_root)

        try:
            # Start Flask application
            self.flask_process = subprocess.Popen(
                [sys.executable, "app.py"], cwd=self.project_root, env=env
            )

            # Wait a moment for Flask to start
            time.sleep(3)

            # Check if Flask is running
            if self.flask_process.poll() is None:
                self.log("ShAI is running successfully!", "SUCCESS")
                return True
            else:
                self.log("Flask application failed to start", "ERROR")
                return False

        except Exception as e:
            self.log(f"Failed to start Flask application: {e}", "ERROR")
            return False

    def open_browser(self, port=5000):
        """Open browser to the application"""
        url = f"http://localhost:{port}"
        self.log(f"Opening browser to {url}", "INFO")

        def open_delayed():
            time.sleep(2)  # Give Flask time to fully start
            try:
                webbrowser.open(url)
            except:
                self.log(f"Couldn't open browser automatically. Visit: {url}", "INFO")

        threading.Thread(target=open_delayed, daemon=True).start()

    def cleanup(self, signum=None, frame=None):
        """Clean up processes on exit"""
        self.log("Shutting down ShAI...", "INFO")

        if self.flask_process and self.flask_process.poll() is None:
            self.log("Stopping Flask application...", "INFO")
            self.flask_process.terminate()
            try:
                self.flask_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.flask_process.kill()

        if self.ollama_process and self.ollama_process.poll() is None:
            self.log("Stopping Ollama service...", "INFO")
            self.ollama_process.terminate()
            try:
                self.ollama_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.ollama_process.kill()

        self.log("ShAI stopped successfully", "SUCCESS")
        sys.exit(0)

    def start(self, force_mode=None):
        """Main start function"""
        # Register signal handlers for cleanup
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)

        self.log("🚀 Starting ShAI (Shae-I) - Your AI Pickup Line Generator", "SUCCESS")

        # Determine mode
        if force_mode:
            mode = force_mode
            self.log(f"Forced to {mode} mode", "INFO")
        else:
            mode = self.check_environment()
            if not mode:
                sys.exit(1)

        # Setup based on mode
        if mode == "local":
            self.log("Setting up local development environment...", "INFO")

            if not self.check_ollama():
                self.log("Ollama setup failed. Cannot continue in local mode.", "ERROR")
                sys.exit(1)

            if not self.check_ollama_model():
                self.log("Ollama model setup failed. Cannot continue.", "ERROR")
                sys.exit(1)

        elif mode == "production":
            self.log("Running in production mode with Claude API", "INFO")

        # Start Flask application
        if not self.start_flask_app(mode):
            self.log("Failed to start application", "ERROR")
            self.cleanup()
            sys.exit(1)

        # Open browser
        self.open_browser()

        # Show success message and instructions
        self.log("=" * 60, "SUCCESS")
        self.log("🎉 ShAI is now running!", "SUCCESS")
        self.log("📱 Visit: http://localhost:5000", "INFO")
        self.log("🎯 Start generating amazing pickup lines!", "INFO")
        self.log("⌨️  Press Ctrl+C to stop", "WARNING")
        self.log("=" * 60, "SUCCESS")

        # Keep the script running
        try:
            while True:
                if self.flask_process.poll() is not None:
                    self.log("Flask application stopped unexpectedly", "ERROR")
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()


def main():
    parser = argparse.ArgumentParser(description="ShAI Quick Start Script")
    parser.add_argument("--local", action="store_true", help="Force local mode")
    parser.add_argument(
        "--production", action="store_true", help="Force production mode"
    )

    args = parser.parse_args()

    starter = ShAIStarter()

    if args.local:
        starter.start("local")
    elif args.production:
        starter.start("production")
    else:
        starter.start()


if __name__ == "__main__":
    main()
