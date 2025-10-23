import os
import json
import requests
import uuid
from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "shae-ai-secret-key-2024")

# History storage configuration
HISTORY_FILE = "history.json"

# Configuration
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
USE_LOCAL = os.environ.get("USE_LOCAL", "false").lower() == "true"


class PickupLineGenerator:
    def __init__(self):
        self.claude_api_url = "https://api.anthropic.com/v1/messages"
        self.ollama_api_url = f"{OLLAMA_URL}/api/generate"

    def generate_with_claude(self, user_input):
        """Generate pickup lines using Claude Haiku"""
        if not CLAUDE_API_KEY:
            raise Exception("Claude API key not configured")

        headers = {
            "x-api-key": CLAUDE_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        prompt = f"""You are ShAI (pronounced "Shae-I"), a playful, charming, and creative AI that crafts clever, funny, and heartfelt pickup lines.

        Based on this input: "{user_input}"

        Generate between 3 and 7 unique pickup lines that are:
        - Flirty, witty, and confident
        - super Personalized to the input
        - Balanced between humor and genuine charm
        - Fresh and natural (avoid clichés)

        Format your response strictly as a JSON array of strings, for example:
        ["pickup line 1", "pickup line 2", "pickup line 3"]

        Do not include any text outside the JSON array."""

        data = {
            "model": "claude-3-5-haiku-20241022",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": prompt}],
        }

        try:
            response = requests.post(
                self.claude_api_url, headers=headers, json=data, timeout=30
            )
            response.raise_for_status()

            result = response.json()
            content = result["content"][0]["text"].strip()

            # Try to parse JSON response
            try:
                pickup_lines = json.loads(content)
                return pickup_lines if isinstance(pickup_lines, list) else [content]
            except json.JSONDecodeError:
                # Fallback: split by newlines if JSON parsing fails
                lines = [line.strip() for line in content.split("\n") if line.strip()]
                return lines[:5]  # Limit to 5 lines

        except Exception as e:
            logger.error(f"Claude API error: {str(e)}")
            raise Exception(f"Failed to generate pickup lines: {str(e)}")

    def generate_with_ollama(self, user_input):
        """Generate pickup lines using Ollama local model"""
        prompt = f"""You are ShAI (pronounced Shae-I), a fun AI that generates creative and witty pickup lines.

Based on this input: "{user_input}"

Generate 3-5 clever, funny, and charming pickup lines. Make them creative and personalized to the input when possible.
Keep them playful and lighthearted, not creepy or inappropriate.

Return each pickup line on a separate line."""

        data = {
            "model": "llama2",  # You can change this to whatever model you have installed
            "prompt": prompt,
            "stream": False,
        }

        try:
            response = requests.post(self.ollama_api_url, json=data, timeout=60)
            response.raise_for_status()

            result = response.json()
            content = result.get("response", "").strip()

            # Split response into lines and clean them up
            lines = [line.strip() for line in content.split("\n") if line.strip()]
            # Remove any numbering or bullet points
            cleaned_lines = []
            for line in lines:
                # Remove common prefixes like "1.", "•", "-", etc.
                cleaned_line = line
                if line and (
                    line[0].isdigit() or line.startswith("•") or line.startswith("-")
                ):
                    cleaned_line = line[2:].strip() if len(line) > 2 else line
                if cleaned_line:
                    cleaned_lines.append(cleaned_line)

            return cleaned_lines[:5]  # Limit to 5 lines

        except requests.exceptions.ConnectionError:
            raise Exception(
                "Cannot connect to Ollama. Make sure it's running on localhost:11434"
            )
        except Exception as e:
            logger.error(f"Ollama API error: {str(e)}")
            raise Exception(f"Failed to generate pickup lines: {str(e)}")

    def generate_pickup_lines(self, user_input):
        """Main method to generate pickup lines"""
        if not user_input or not user_input.strip():
            return [
                "Hey, are you my appendix? Because I don't understand how you work but this feeling in my stomach makes me want to take you out."
            ]

        try:
            if USE_LOCAL:
                return self.generate_with_ollama(user_input)
            else:
                return self.generate_with_claude(user_input)
        except Exception as e:
            logger.error(f"Error generating pickup lines: {str(e)}")
            # Fallback pickup lines if AI fails
            fallback_lines = [
                "Are you Wi-Fi? Because I'm really feeling a connection.",
                "Do you have a map? Because I just got lost in your eyes.",
                "Are you a magician? Because whenever I look at you, everyone else disappears.",
                "Is your name Google? Because you have everything I've been searching for.",
                "Are you a parking ticket? Because you've got 'fine' written all over you.",
            ]
            return fallback_lines[:3]


# Initialize the generator
generator = PickupLineGenerator()


class HistoryManager:
    def __init__(self, history_file):
        self.history_file = history_file
        self.ensure_history_file()

    def ensure_history_file(self):
        """Ensure the history file exists"""
        if not os.path.exists(self.history_file):
            with open(self.history_file, "w") as f:
                json.dump([], f)

    def get_session_id(self):
        """Get or create a session ID"""
        if "session_id" not in session:
            session["session_id"] = str(uuid.uuid4())
        return session["session_id"]

    def add_to_history(self, session_id, user_input, pickup_lines, timestamp):
        """Add a generation to history"""
        try:
            with open(self.history_file, "r") as f:
                history = json.load(f)

            history_entry = {
                "id": str(uuid.uuid4()),
                "session_id": session_id,
                "user_input": user_input,
                "pickup_lines": pickup_lines,
                "timestamp": timestamp,
                "using_local": USE_LOCAL,
            }

            history.append(history_entry)

            # Keep only the last 100 entries to prevent file from growing too large
            if len(history) > 100:
                history = history[-100:]

            with open(self.history_file, "w") as f:
                json.dump(history, f, indent=2)

            return history_entry
        except Exception as e:
            logger.error(f"Error adding to history: {str(e)}")
            return None

    def get_history(self, session_id):
        """Get history for a specific session"""
        try:
            with open(self.history_file, "r") as f:
                history = json.load(f)

            # Filter by session ID and return most recent first
            session_history = [
                entry for entry in history if entry.get("session_id") == session_id
            ]
            return sorted(session_history, key=lambda x: x["timestamp"], reverse=True)
        except Exception as e:
            logger.error(f"Error reading history: {str(e)}")
            return []

    def clear_history(self, session_id):
        """Clear history for a specific session"""
        try:
            with open(self.history_file, "r") as f:
                history = json.load(f)

            # Remove entries for this session
            history = [
                entry for entry in history if entry.get("session_id") != session_id
            ]

            with open(self.history_file, "w") as f:
                json.dump(history, f, indent=2)

            return True
        except Exception as e:
            logger.error(f"Error clearing history: {str(e)}")
            return False


# Initialize the history manager
history_manager = HistoryManager(HISTORY_FILE)


@app.route("/")
def index():
    """Main page"""
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate_pickup_lines():
    """API endpoint to generate pickup lines"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        user_input = data.get("input", "").strip()
        if not user_input:
            return jsonify({"error": "No input provided"}), 400

        # Generate pickup lines
        pickup_lines = generator.generate_pickup_lines(user_input)

        timestamp = datetime.now().isoformat()
        session_id = history_manager.get_session_id()

        # Add to history
        history_entry = history_manager.add_to_history(
            session_id, user_input, pickup_lines, timestamp
        )

        response = {
            "success": True,
            "input": user_input,
            "pickup_lines": pickup_lines,
            "timestamp": timestamp,
            "using_local": USE_LOCAL,
            "history_id": history_entry["id"] if history_entry else None,
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error in generate endpoint: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/history", methods=["GET"])
def get_history():
    """Get history for the current session"""
    try:
        session_id = history_manager.get_session_id()
        history = history_manager.get_history(session_id)

        return jsonify({"success": True, "history": history, "session_id": session_id})
    except Exception as e:
        logger.error(f"Error in history endpoint: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/history", methods=["DELETE"])
def clear_history():
    """Clear history for the current session"""
    try:
        session_id = history_manager.get_session_id()
        success = history_manager.clear_history(session_id)

        if success:
            return jsonify({"success": True, "message": "History cleared successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to clear history"}), 500
    except Exception as e:
        logger.error(f"Error clearing history: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "using_local": USE_LOCAL,
            "claude_configured": bool(CLAUDE_API_KEY),
        }
    )


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500


if __name__ == "__main__":
    # For local development
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "true").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
