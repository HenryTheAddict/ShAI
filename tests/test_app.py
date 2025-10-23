#!/usr/bin/env python3
"""
ShAI Application Tests

Basic test suite for the ShAI (Shae-I) AI pickup line generator.
Tests the Flask application functionality, API endpoints, and error handling.

Run with:
    pytest tests/test_app.py -v
    python -m pytest tests/test_app.py
"""

import pytest
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the app
from app import app, PickupLineGenerator


class TestShAIApp:
    """Test cases for the main ShAI Flask application"""

    @pytest.fixture
    def client(self):
        """Create a test client for the Flask application"""
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test-secret-key"
        with app.test_client() as client:
            yield client

    @pytest.fixture
    def mock_generator(self):
        """Mock pickup line generator for testing"""
        generator = PickupLineGenerator()
        return generator

    def test_app_configuration(self):
        """Test that the app is properly configured"""
        assert app is not None
        assert app.config["TESTING"] is True

    def test_index_route(self, client):
        """Test the main index page loads correctly"""
        response = client.get("/")
        assert response.status_code == 200
        assert b"ShAI" in response.data
        assert b"Pickup Line Generator" in response.data

    def test_health_endpoint(self, client):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] == "healthy"

    def test_generate_endpoint_success(self, client):
        """Test successful pickup line generation"""
        with patch.object(
            PickupLineGenerator, "generate_pickup_lines"
        ) as mock_generate:
            mock_generate.return_value = [
                "Are you a magician? Because whenever I look at you, everyone else disappears.",
                "Do you have a map? Because I just got lost in your eyes.",
                "Are you Wi-Fi? Because I'm really feeling a connection.",
            ]

            response = client.post(
                "/generate",
                data=json.dumps({"input": "I am at a coffee shop"}),
                content_type="application/json",
            )

            assert response.status_code == 200
            data = json.loads(response.data)

            assert data["success"] is True
            assert "pickup_lines" in data
            assert len(data["pickup_lines"]) == 3
            assert "timestamp" in data
            assert data["input"] == "I am at a coffee shop"

    def test_generate_endpoint_no_input(self, client):
        """Test generation endpoint with no input"""
        response = client.post(
            "/generate", data=json.dumps({"input": ""}), content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_generate_endpoint_no_data(self, client):
        """Test generation endpoint with no JSON data"""
        response = client.post("/generate", data="", content_type="application/json")

        assert response.status_code == 400

    def test_generate_endpoint_invalid_json(self, client):
        """Test generation endpoint with invalid JSON"""
        response = client.post(
            "/generate", data="invalid json", content_type="application/json"
        )

        assert response.status_code == 400

    def test_generate_endpoint_server_error(self, client):
        """Test generation endpoint when AI service fails"""
        with patch.object(
            PickupLineGenerator, "generate_pickup_lines"
        ) as mock_generate:
            mock_generate.side_effect = Exception("API service unavailable")

            response = client.post(
                "/generate",
                data=json.dumps({"input": "test input"}),
                content_type="application/json",
            )

            assert response.status_code == 500
            data = json.loads(response.data)
            assert data["success"] is False
            assert "error" in data

    def test_404_error_handler(self, client):
        """Test custom 404 error page"""
        response = client.get("/nonexistent-page")
        assert response.status_code == 404
        assert b"404" in response.data

    def test_500_error_handler(self, client):
        """Test custom 500 error page"""
        with patch("app.render_template") as mock_render:
            mock_render.side_effect = Exception("Template error")

            # This should trigger a 500 error
            response = client.get("/health")
            assert response.status_code == 500


class TestPickupLineGenerator:
    """Test cases for the PickupLineGenerator class"""

    @pytest.fixture
    def generator(self):
        """Create a PickupLineGenerator instance"""
        return PickupLineGenerator()

    def test_generator_initialization(self, generator):
        """Test that the generator initializes correctly"""
        assert generator is not None
        assert hasattr(generator, "claude_api_url")
        assert hasattr(generator, "ollama_api_url")

    def test_empty_input_fallback(self, generator):
        """Test fallback behavior for empty input"""
        result = generator.generate_pickup_lines("")
        assert isinstance(result, list)
        assert len(result) > 0
        # Should return at least one fallback line
        assert any("appendix" in line.lower() for line in result)

    def test_whitespace_input_fallback(self, generator):
        """Test fallback behavior for whitespace-only input"""
        result = generator.generate_pickup_lines("   \n   ")
        assert isinstance(result, list)
        assert len(result) > 0

    @patch("requests.post")
    def test_claude_api_success(self, mock_post, generator):
        """Test successful Claude API call"""
        # Mock successful Claude API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "content": [{"text": '["Line 1", "Line 2", "Line 3"]'}]
        }
        mock_post.return_value = mock_response

        with patch.dict(
            os.environ, {"CLAUDE_API_KEY": "test-key", "USE_LOCAL": "false"}
        ):
            result = generator.generate_with_claude("test input")
            assert isinstance(result, list)
            assert len(result) == 3

    @patch("requests.post")
    def test_claude_api_failure(self, mock_post, generator):
        """Test Claude API failure handling"""
        mock_post.side_effect = Exception("API Error")

        with patch.dict(os.environ, {"CLAUDE_API_KEY": "test-key"}):
            with pytest.raises(Exception):
                generator.generate_with_claude("test input")

    @patch("requests.post")
    def test_ollama_api_success(self, mock_post, generator):
        """Test successful Ollama API call"""
        # Mock successful Ollama API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"response": "Line 1\nLine 2\nLine 3"}
        mock_post.return_value = mock_response

        result = generator.generate_with_ollama("test input")
        assert isinstance(result, list)
        assert len(result) >= 1

    @patch("requests.post")
    def test_ollama_api_connection_error(self, mock_post, generator):
        """Test Ollama connection error handling"""
        import requests

        mock_post.side_effect = requests.exceptions.ConnectionError()

        with pytest.raises(Exception) as exc_info:
            generator.generate_with_ollama("test input")

        assert "Cannot connect to Ollama" in str(exc_info.value)

    def test_generate_pickup_lines_fallback(self, generator):
        """Test fallback mechanism when AI services fail"""
        with patch.object(generator, "generate_with_claude") as mock_claude:
            with patch.object(generator, "generate_with_ollama") as mock_ollama:
                # Make both methods fail
                mock_claude.side_effect = Exception("API Error")
                mock_ollama.side_effect = Exception("Ollama Error")

                # Should still return fallback lines
                result = generator.generate_pickup_lines("test input")
                assert isinstance(result, list)
                assert len(result) > 0
                # Should contain some of the fallback lines
                fallback_keywords = ["wi-fi", "connection", "map", "eyes", "magician"]
                assert any(
                    keyword in " ".join(result).lower() for keyword in fallback_keywords
                )


class TestEnvironmentConfiguration:
    """Test environment variable handling and configuration"""

    def test_local_configuration(self):
        """Test local development configuration"""
        with patch.dict(os.environ, {"USE_LOCAL": "true"}):
            # Reload the module to pick up env changes
            import importlib
            import app

            importlib.reload(app)

            assert os.environ.get("USE_LOCAL").lower() == "true"

    def test_production_configuration(self):
        """Test production configuration"""
        with patch.dict(
            os.environ, {"USE_LOCAL": "false", "CLAUDE_API_KEY": "test-key"}
        ):
            # Reload the module to pick up env changes
            import importlib
            import app

            importlib.reload(app)

            assert os.environ.get("USE_LOCAL").lower() == "false"
            assert os.environ.get("CLAUDE_API_KEY") == "test-key"

    def test_missing_claude_key_handling(self):
        """Test handling when Claude API key is missing"""
        with patch.dict(os.environ, {"USE_LOCAL": "false"}, clear=True):
            generator = PickupLineGenerator()

            with pytest.raises(Exception) as exc_info:
                generator.generate_with_claude("test")

            assert "Claude API key not configured" in str(exc_info.value)


class TestUtilityFunctions:
    """Test utility functions and edge cases"""

    def test_json_parsing_fallback(self):
        """Test JSON parsing with fallback to text splitting"""
        generator = PickupLineGenerator()

        # Test with non-JSON response
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "content": [{"text": "Line 1\nLine 2\nLine 3"}]  # Not JSON format
            }
            mock_post.return_value = mock_response

            with patch.dict(os.environ, {"CLAUDE_API_KEY": "test-key"}):
                result = generator.generate_with_claude("test")
                assert isinstance(result, list)
                assert len(result) >= 1

    def test_ollama_response_cleaning(self):
        """Test cleaning of numbered/bulleted responses from Ollama"""
        generator = PickupLineGenerator()

        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "response": "1. First line\n2. Second line\n• Third line\n- Fourth line"
            }
            mock_post.return_value = mock_response

            result = generator.generate_with_ollama("test")
            assert isinstance(result, list)
            # Check that numbering/bullets are removed
            assert not any(line.startswith(("1.", "2.", "•", "-")) for line in result)


if __name__ == "__main__":
    """Run tests directly"""
    pytest.main([__file__, "-v"])
