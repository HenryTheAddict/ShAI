#!/usr/bin/env python3
"""
WSGI configuration for ShAI application.

This module contains the WSGI callable used by WSGI servers to serve the application.
For Namecheap shared hosting and other production environments.
"""

import sys
import os
from pathlib import Path

# Add the project directory to the Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv

    env_path = project_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # dotenv not available, environment variables should be set by hosting provider
    pass

# Set default environment variables for production
os.environ.setdefault("FLASK_ENV", "production")
os.environ.setdefault("DEBUG", "false")

# Import the Flask application
try:
    from app import app as application
except ImportError as e:
    # Fallback error handling
    print(f"Error importing application: {e}")

    # Create a minimal error application
    from flask import Flask, jsonify

    application = Flask(__name__)

    @application.route("/")
    def error():
        return jsonify(
            {
                "error": "Application failed to load",
                "message": "Please check the server configuration and try again.",
            }
        ), 500


# Configure logging for production
import logging
from logging.handlers import RotatingFileHandler

if not application.debug:
    # Set up file logging
    log_dir = project_dir / "logs"
    log_dir.mkdir(exist_ok=True)

    file_handler = RotatingFileHandler(
        log_dir / "shai.log",
        maxBytes=10240000,  # 10MB
        backupCount=10,
    )
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        )
    )
    file_handler.setLevel(logging.INFO)
    application.logger.addHandler(file_handler)

    application.logger.setLevel(logging.INFO)
    application.logger.info("ShAI application startup")

# Ensure the application object is available
if __name__ == "__main__":
    application.run()
