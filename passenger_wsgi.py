#!/usr/bin/env python3
"""
Enhanced Passenger WSGI configuration for ShAI application.

This file is specifically designed for Namecheap shared hosting and other
hosting providers that use Passenger WSGI with robust error handling.

Features:
- ASCII-only logging (no Unicode issues)
- Robust dependency handling
- Comprehensive error pages without Flask dependency
- Automatic initialization with fallbacks
- Detailed diagnostics and debugging
"""

import sys
import os
import logging
from pathlib import Path
import traceback
import json
from datetime import datetime

# Get the project directory
PROJECT_HOME = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_HOME))

# Configure logging with ASCII-only formatting to avoid encoding issues
LOG_DIR = PROJECT_HOME / "logs"
LOG_DIR.mkdir(exist_ok=True)


# Create a custom formatter that avoids Unicode issues
class ASCIIFormatter(logging.Formatter):
    def format(self, record):
        # Replace any Unicode characters that might cause issues
        msg = super().format(record)
        # Convert to ASCII, ignoring problematic characters
        return msg.encode("ascii", errors="ignore").decode("ascii")


# Setup logging with ASCII-only formatter
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler(LOG_DIR / "passenger_wsgi.log")
file_handler.setLevel(logging.INFO)
file_formatter = ASCIIFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = ASCIIFormatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


def setup_environment():
    """Setup environment variables for production deployment."""
    logger.info("Setting up environment for hosting deployment...")

    # Set default production environment
    os.environ.setdefault("FLASK_ENV", "production")
    os.environ.setdefault("DEBUG", "false")
    os.environ.setdefault("USE_LOCAL", "false")

    # Load environment variables from .env file if it exists
    env_file = PROJECT_HOME / ".env"
    if env_file.exists():
        logger.info("Loading environment from .env file")
        try:
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        if key not in os.environ:
                            os.environ[key] = value.strip("\"'")
                            logger.info("Loaded environment variable: %s", key)
        except Exception as e:
            logger.error("Error loading .env file: %s", str(e))
    else:
        logger.warning(".env file not found - relying on hosting provider environment")

    # Ensure critical environment variables are set
    required_vars = {
        "SECRET_KEY": "shared-hosting-shai-secret-key-change-in-production",
        "FLASK_ENV": "production",
        "USE_LOCAL": "false",
    }

    for var, default in required_vars.items():
        if not os.environ.get(var):
            os.environ[var] = default
            logger.warning("Set default value for %s", var)


def check_dependencies():
    """Check if all required dependencies are available."""
    required_modules = ["flask", "requests"]
    missing_modules = []
    available_modules = []

    for module in required_modules:
        try:
            __import__(module)
            available_modules.append(module)
            logger.info("Module %s is available", module)
        except ImportError:
            missing_modules.append(module)
            logger.error("Module %s is missing", module)

    return missing_modules, available_modules


def create_minimal_wsgi_app():
    """Create a minimal WSGI application without external dependencies."""

    def application(environ, start_response):
        """Minimal WSGI application for error display."""

        path = environ.get("PATH_INFO", "/")
        method = environ.get("REQUEST_METHOD", "GET")

        # Simple routing
        if path == "/health":
            return handle_health(environ, start_response)
        elif path == "/debug":
            return handle_debug(environ, start_response)
        else:
            return handle_error_page(environ, start_response)

    return application


def handle_health(environ, start_response):
    """Handle health check endpoint."""
    missing_deps, available_deps = check_dependencies()

    health_data = {
        "status": "error" if missing_deps else "healthy",
        "message": "Missing dependencies" if missing_deps else "Application ready",
        "missing_dependencies": missing_deps,
        "available_dependencies": available_deps,
        "environment": os.environ.get("FLASK_ENV"),
        "timestamp": datetime.now().isoformat(),
        "claude_configured": bool(os.environ.get("CLAUDE_API_KEY"))
        and os.environ.get("CLAUDE_API_KEY") != "your-claude-api-key-here",
    }

    response_body = json.dumps(health_data, indent=2).encode("utf-8")

    status = "500 Internal Server Error" if missing_deps else "200 OK"
    headers = [
        ("Content-Type", "application/json"),
        ("Content-Length", str(len(response_body))),
    ]

    start_response(status, headers)
    return [response_body]


def handle_debug(environ, start_response):
    """Handle debug information endpoint."""
    missing_deps, available_deps = check_dependencies()

    debug_info = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "project_home": str(PROJECT_HOME),
        "environment_vars": {
            k: v if "KEY" not in k and "SECRET" not in k else "***HIDDEN***"
            for k, v in os.environ.items()
            if k.startswith(("FLASK_", "CLAUDE_", "USE_", "DEBUG", "SECRET"))
        },
        "missing_dependencies": missing_deps,
        "available_dependencies": available_deps,
        "python_path": sys.path[:5],
        "timestamp": datetime.now().isoformat(),
    }

    response_body = json.dumps(debug_info, indent=2).encode("utf-8")

    headers = [
        ("Content-Type", "application/json"),
        ("Content-Length", str(len(response_body))),
    ]

    start_response("200 OK", headers)
    return [response_body]


def handle_error_page(environ, start_response):
    """Handle main error page display."""
    missing_deps, available_deps = check_dependencies()

    # Create a comprehensive error page
    error_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShAI - Initialization Error</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 40px;
            max-width: 800px;
            margin: 0 auto;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        .logo {{
            font-size: 3rem;
            font-weight: bold;
            margin-bottom: 20px;
            text-align: center;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .error {{
            background: rgba(255,0,0,0.2);
            border: 1px solid rgba(255,0,0,0.3);
            color: #ffcccc;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .info {{
            background: rgba(0,255,255,0.2);
            border: 1px solid rgba(0,255,255,0.3);
            color: #ccffff;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .success {{
            background: rgba(0,255,0,0.2);
            border: 1px solid rgba(0,255,0,0.3);
            color: #ccffcc;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .code {{
            background: rgba(0,0,0,0.3);
            padding: 15px;
            border-radius: 5px;
            font-family: monospace;
            overflow-x: auto;
            margin: 10px 0;
        }}
        .timestamp {{
            text-align: center;
            font-size: 0.8em;
            opacity: 0.7;
            margin-top: 20px;
        }}
        ul, ol {{
            text-align: left;
        }}
        .btn {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            text-decoration: none;
            margin: 5px;
            border: 1px solid rgba(255,255,255,0.3);
        }}
        .btn:hover {{
            background: rgba(255,255,255,0.3);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">ShAI</div>
        <h1>Application Initialization Status</h1>

        {"<div class='error'>" if missing_deps else "<div class='success'>"}
            <h3>{"Dependencies Missing" if missing_deps else "Dependencies Check Passed"}</h3>
            {"<p>The following Python packages are required but not installed:</p>" if missing_deps else "<p>All required dependencies are available.</p>"}
            {f"<div class='code'>{', '.join(missing_deps)}</div>" if missing_deps else ""}
        </div>

        {f"<div class='success'><h4>Available Dependencies:</h4><div class='code'>{', '.join(available_deps)}</div></div>" if available_deps else ""}

        <div class="info">
            <h4>System Information:</h4>
            <ul>
                <li><strong>Python Version:</strong> {sys.version.split()[0]}</li>
                <li><strong>Project Path:</strong> {PROJECT_HOME}</li>
                <li><strong>Environment:</strong> {os.environ.get("FLASK_ENV", "unknown")}</li>
                <li><strong>Claude API:</strong> {"Configured" if os.environ.get("CLAUDE_API_KEY") and os.environ.get("CLAUDE_API_KEY") != "your-claude-api-key-here" else "Not configured"}</li>
            </ul>
        </div>

        {"<div class='info'>" if missing_deps else ""}
            {"<h4>Installation Instructions:</h4>" if missing_deps else ""}
            {"<ol>" if missing_deps else ""}
                {"<li><strong>SSH/Terminal Method:</strong><div class='code'>pip install --user flask requests gunicorn</div></li>" if missing_deps else ""}
                {"<li><strong>cPanel Method:</strong><br>Go to 'Python Selector' → Select your app → 'Packages' → Install: flask, requests</li>" if missing_deps else ""}
                {"<li><strong>Upload Method:</strong><br>Upload requirements.txt and use hosting control panel to install packages</li>" if missing_deps else ""}
            {"</ol>" if missing_deps else ""}
        {"</div>" if missing_deps else ""}

        <div class="info">
            <h4>Quick Actions:</h4>
            <a href="/health" class="btn">Health Check (JSON)</a>
            <a href="/debug" class="btn">Debug Info (JSON)</a>
            <a href="/" class="btn">Refresh Status</a>
        </div>

        <div class="timestamp">
            Status checked at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
        </div>
    </div>
</body>
</html>"""

    response_body = error_html.encode("utf-8")

    headers = [
        ("Content-Type", "text/html"),
        ("Content-Length", str(len(response_body))),
    ]

    status = "500 Internal Server Error" if missing_deps else "200 OK"
    start_response(status, headers)
    return [response_body]


def initialize_main_app():
    """Initialize the main ShAI application."""
    logger.info("Attempting to initialize main ShAI application...")

    try:
        # Check dependencies first
        missing_deps, available_deps = check_dependencies()
        if missing_deps:
            raise ImportError(
                f"Missing required dependencies: {', '.join(missing_deps)}"
            )

        # Import and configure the main application
        from app import app as main_app

        # Configure for production
        main_app.config.update(
            {
                "DEBUG": os.environ.get("DEBUG", "false").lower() == "true",
                "TESTING": False,
                "SECRET_KEY": os.environ.get("SECRET_KEY", "change-this-secret-key"),
            }
        )

        # Verify critical configuration
        claude_key = os.environ.get("CLAUDE_API_KEY")
        if not claude_key or claude_key == "your-claude-api-key-here":
            logger.warning("CLAUDE_API_KEY not properly configured")
        else:
            logger.info("CLAUDE_API_KEY is configured")

        # Test a simple route to ensure app is working
        with main_app.test_client() as client:
            response = client.get("/health")
            if response.status_code == 200:
                logger.info("Main application health check passed")
            else:
                logger.warning("Health check returned status %d", response.status_code)

        logger.info("Main ShAI application initialized successfully")
        return main_app

    except Exception as e:
        logger.error("Failed to initialize main application: %s", str(e))
        logger.error("Traceback: %s", traceback.format_exc())
        raise


def auto_initialize():
    """Auto-initialize the application with comprehensive error handling."""
    logger.info("=" * 60)
    logger.info("ShAI Passenger WSGI Auto-Initialization Starting...")
    logger.info("Project Home: %s", PROJECT_HOME)
    logger.info("Python Version: %s", sys.version)
    logger.info("Platform: %s", sys.platform)
    logger.info("=" * 60)

    try:
        # Step 1: Setup environment
        setup_environment()

        # Step 2: Check dependencies
        missing_deps, available_deps = check_dependencies()

        if missing_deps:
            logger.warning("Missing dependencies detected: %s", ", ".join(missing_deps))
            logger.info(
                "Creating minimal WSGI app with dependency installation instructions"
            )
            return create_minimal_wsgi_app()

        # Step 3: Initialize main application
        app = initialize_main_app()

        logger.info("ShAI application auto-initialization completed successfully!")
        logger.info("Application is ready to serve requests")
        return app

    except Exception as e:
        logger.error("Auto-initialization failed: %s", str(e))
        logger.error("Full traceback: %s", traceback.format_exc())

        # Create minimal fallback application
        logger.info("Creating minimal fallback application...")
        return create_minimal_wsgi_app()


# Auto-initialize the application when this module is imported
logger.info("Passenger WSGI module loaded - starting auto-initialization...")

try:
    application = auto_initialize()
except Exception as critical_error:
    logger.error("Critical error during initialization: %s", str(critical_error))
    logger.error("Creating emergency fallback application")
    application = create_minimal_wsgi_app()

# Ensure we have a valid WSGI application
if application is None:
    logger.error("Critical error: No application created!")
    application = create_minimal_wsgi_app()

# Log final status
logger.info("Passenger WSGI configuration complete")
logger.info("Application type: %s", type(application).__name__)
