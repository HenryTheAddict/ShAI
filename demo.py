#!/usr/bin/env python3
"""
ShAI (Shae-I) Demo Script

A demonstration script for the AI-powered pickup line generator.
Shows off the capabilities of ShAI in both local and production modes.

Usage:
    python demo.py                 # Run interactive demo
    python demo.py --examples      # Show example scenarios
    python demo.py --test-api      # Test API endpoints
    python demo.py --benchmark     # Performance benchmark
    python demo.py --help          # Show help
"""

import os
import sys
import time
import json
import argparse
import requests
from pathlib import Path
from typing import List, Dict, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Try to import the app components
try:
    from app import PickupLineGenerator

    APP_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import app components: {e}")
    APP_AVAILABLE = False


class ShAIDemo:
    """Demo class for showcasing ShAI functionality"""

    def __init__(self):
        self.generator = None
        if APP_AVAILABLE:
            self.generator = PickupLineGenerator()

        # Demo scenarios
        self.demo_scenarios = [
            {
                "name": "Coffee Shop",
                "input": "I'm at a coffee shop and there's someone cute reading a book",
                "description": "Classic coffee shop scenario - bookworm edition",
            },
            {
                "name": "Gym",
                "input": "At the gym, someone is doing impressive workouts",
                "description": "Fitness-focused pickup lines for active people",
            },
            {
                "name": "Library",
                "input": "In a quiet library, studying for exams",
                "description": "Intellectual and study-themed approaches",
            },
            {
                "name": "Dog Park",
                "input": "At the dog park with cute dogs and their owners",
                "description": "Pet-friendly conversation starters",
            },
            {
                "name": "Art Gallery",
                "input": "At an art gallery opening, appreciating creativity",
                "description": "Cultured and artistic pickup lines",
            },
            {
                "name": "Beach",
                "input": "Sunny beach day, everyone's relaxing and having fun",
                "description": "Summer vibes and beach-themed lines",
            },
            {
                "name": "Bookstore",
                "input": "Browsing books in a cozy independent bookstore",
                "description": "Literary and intellectual conversation starters",
            },
            {
                "name": "Cooking Class",
                "input": "Taking a cooking class, learning to make pasta",
                "description": "Food and cooking themed pickup lines",
            },
        ]

    def print_header(self):
        """Print a fancy header for the demo"""
        print("=" * 70)
        print("🎯 ShAI (Shae-I) - AI Pickup Line Generator Demo")
        print("=" * 70)
        print("✨ Turn any situation into smooth conversation starters!")
        print("🤖 Powered by AI - Claude Haiku & Ollama")
        print("=" * 70)
        print()

    def print_colored(self, text: str, color: str = "default"):
        """Print colored text for better visibility"""
        colors = {
            "red": "\033[91m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "purple": "\033[95m",
            "cyan": "\033[96m",
            "default": "\033[0m",
        }

        color_code = colors.get(color, colors["default"])
        reset = colors["default"]
        print(f"{color_code}{text}{reset}")

    def show_configuration(self):
        """Show current configuration"""
        print("🔧 Current Configuration:")
        print("-" * 30)

        use_local = os.environ.get("USE_LOCAL", "false").lower() == "true"
        claude_key = os.environ.get("CLAUDE_API_KEY", "")

        if use_local:
            self.print_colored("✓ Mode: Local Development (Ollama)", "green")
            self.print_colored(
                f"✓ Ollama URL: {os.environ.get('OLLAMA_URL', 'http://localhost:11434')}",
                "blue",
            )
        else:
            self.print_colored("✓ Mode: Production (Claude API)", "green")
            if claude_key and claude_key != "your-claude-api-key-here":
                self.print_colored("✓ Claude API: Configured", "green")
            else:
                self.print_colored("⚠️  Claude API: Not configured", "yellow")

        print()

    def test_connectivity(self):
        """Test connectivity to AI services"""
        print("🔍 Testing Connectivity:")
        print("-" * 30)

        use_local = os.environ.get("USE_LOCAL", "false").lower() == "true"

        if use_local:
            try:
                response = requests.get("http://localhost:11434", timeout=5)
                if response.status_code == 200:
                    self.print_colored("✓ Ollama service is running", "green")
                else:
                    self.print_colored(
                        "⚠️  Ollama service responded with error", "yellow"
                    )
            except requests.exceptions.ConnectionError:
                self.print_colored("❌ Cannot connect to Ollama (not running?)", "red")
            except Exception as e:
                self.print_colored(f"❌ Ollama connection error: {e}", "red")
        else:
            claude_key = os.environ.get("CLAUDE_API_KEY", "")
            if claude_key and claude_key != "your-claude-api-key-here":
                self.print_colored("✓ Claude API key is configured", "green")
            else:
                self.print_colored("❌ Claude API key is missing", "red")

        print()

    def generate_demo_lines(self, scenario: Dict) -> Optional[List[str]]:
        """Generate pickup lines for a demo scenario"""
        if not self.generator:
            return None

        try:
            lines = self.generator.generate_pickup_lines(scenario["input"])
            return lines
        except Exception as e:
            self.print_colored(f"❌ Error generating lines: {e}", "red")
            return None

    def run_scenario_demo(self, scenario: Dict):
        """Run a demo for a specific scenario"""
        print(f"📍 Scenario: {scenario['name']}")
        print(f"💭 Situation: {scenario['input']}")
        print(f"📝 Description: {scenario['description']}")
        print()

        self.print_colored("🤖 Generating pickup lines...", "cyan")

        start_time = time.time()
        lines = self.generate_demo_lines(scenario)
        end_time = time.time()

        if lines:
            print()
            self.print_colored("💝 Generated Pickup Lines:", "purple")
            print("-" * 40)

            for i, line in enumerate(lines, 1):
                print(f"  {i}. {line}")

            print()
            self.print_colored(
                f"⚡ Generated {len(lines)} lines in {end_time - start_time:.2f} seconds",
                "blue",
            )
        else:
            self.print_colored("❌ Failed to generate pickup lines", "red")

        print()

    def interactive_mode(self):
        """Run interactive demo mode"""
        print("🎮 Interactive Mode")
        print("=" * 50)
        print("Enter situations and get personalized pickup lines!")
        print("Type 'quit', 'exit', or 'q' to stop.")
        print()

        while True:
            try:
                user_input = input("🎯 Describe your situation: ").strip()

                if user_input.lower() in ["quit", "exit", "q", ""]:
                    print("\n👋 Thanks for trying ShAI! Happy flirting!")
                    break

                print()
                self.print_colored(
                    "🤖 Generating your personalized pickup lines...", "cyan"
                )

                if self.generator:
                    start_time = time.time()
                    lines = self.generator.generate_pickup_lines(user_input)
                    end_time = time.time()

                    if lines:
                        print()
                        self.print_colored("💝 Your Pickup Lines:", "purple")
                        print("-" * 30)

                        for i, line in enumerate(lines, 1):
                            print(f"  {i}. {line}")

                        print()
                        self.print_colored(
                            f"⚡ Generated in {end_time - start_time:.2f} seconds",
                            "blue",
                        )
                    else:
                        self.print_colored(
                            "❌ Failed to generate lines. Try again!", "red"
                        )
                else:
                    self.print_colored(
                        "❌ Generator not available. Check your setup.", "red"
                    )

                print("\n" + "─" * 60 + "\n")

            except KeyboardInterrupt:
                print("\n\n👋 Demo interrupted. Goodbye!")
                break
            except Exception as e:
                self.print_colored(f"❌ Error: {e}", "red")

    def run_examples(self):
        """Run through all example scenarios"""
        print("📚 Example Scenarios Demo")
        print("=" * 50)
        print("Let's see ShAI in action with various situations!\n")

        for i, scenario in enumerate(self.demo_scenarios, 1):
            print(f"[{i}/{len(self.demo_scenarios)}]")
            self.run_scenario_demo(scenario)

            if i < len(self.demo_scenarios):
                try:
                    input(
                        "Press Enter to continue to next scenario (Ctrl+C to stop)..."
                    )
                    print()
                except KeyboardInterrupt:
                    print("\n\n👋 Demo stopped by user.")
                    break

    def test_api_endpoints(self):
        """Test the Flask API endpoints"""
        print("🔗 API Endpoints Test")
        print("=" * 50)

        base_url = "http://localhost:5000"

        # Test health endpoint
        print("Testing /health endpoint...")
        try:
            response = requests.get(f"{base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.print_colored("✓ Health endpoint working", "green")
                print(f"  Status: {data.get('status')}")
                print(f"  Mode: {'Local' if data.get('using_local') else 'Production'}")
            else:
                self.print_colored(
                    f"⚠️  Health endpoint returned {response.status_code}", "yellow"
                )
        except requests.exceptions.ConnectionError:
            self.print_colored("❌ Cannot connect to Flask app (not running?)", "red")
            self.print_colored("   Start with: python app.py", "blue")
            return
        except Exception as e:
            self.print_colored(f"❌ Health check error: {e}", "red")

        print()

        # Test generate endpoint
        print("Testing /generate endpoint...")
        test_data = {"input": "I'm at a coffee shop demo test"}

        try:
            response = requests.post(
                f"{base_url}/generate",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    lines = data.get("pickup_lines", [])
                    self.print_colored("✓ Generate endpoint working", "green")
                    print(f"  Generated {len(lines)} pickup lines")
                    if lines:
                        print(
                            "  Sample line:",
                            lines[0][:50] + "..." if len(lines[0]) > 50 else lines[0],
                        )
                else:
                    self.print_colored("⚠️  Generate endpoint returned error", "yellow")
                    print(f"  Error: {data.get('error')}")
            else:
                self.print_colored(
                    f"❌ Generate endpoint returned {response.status_code}", "red"
                )
                print(f"  Response: {response.text}")
        except Exception as e:
            self.print_colored(f"❌ Generate endpoint error: {e}", "red")

        print()

    def benchmark_performance(self):
        """Benchmark performance of pickup line generation"""
        print("⚡ Performance Benchmark")
        print("=" * 50)

        if not self.generator:
            self.print_colored("❌ Generator not available for benchmarking", "red")
            return

        test_inputs = [
            "coffee shop",
            "gym workout",
            "library study session",
            "art gallery opening",
            "beach volleyball game",
        ]

        print(f"Testing with {len(test_inputs)} different scenarios...")
        print()

        total_time = 0
        successful_runs = 0
        all_results = []

        for i, test_input in enumerate(test_inputs, 1):
            print(f"[{i}/{len(test_inputs)}] Testing: {test_input}")

            try:
                start_time = time.time()
                lines = self.generator.generate_pickup_lines(test_input)
                end_time = time.time()

                duration = end_time - start_time
                total_time += duration
                successful_runs += 1

                all_results.append(
                    {
                        "input": test_input,
                        "duration": duration,
                        "lines_count": len(lines) if lines else 0,
                        "success": True,
                    }
                )

                self.print_colored(
                    f"  ✓ {duration:.2f}s - {len(lines) if lines else 0} lines", "green"
                )

            except Exception as e:
                all_results.append(
                    {
                        "input": test_input,
                        "duration": 0,
                        "lines_count": 0,
                        "success": False,
                        "error": str(e),
                    }
                )
                self.print_colored(f"  ❌ Failed: {e}", "red")

            time.sleep(1)  # Brief pause between requests

        print()
        print("📊 Benchmark Results:")
        print("-" * 30)

        if successful_runs > 0:
            avg_time = total_time / successful_runs
            total_lines = sum(r["lines_count"] for r in all_results if r["success"])

            print(f"Successful runs: {successful_runs}/{len(test_inputs)}")
            print(f"Average response time: {avg_time:.2f} seconds")
            print(f"Total lines generated: {total_lines}")
            print(f"Average lines per request: {total_lines / successful_runs:.1f}")

            fastest = min(
                [r for r in all_results if r["success"]], key=lambda x: x["duration"]
            )
            slowest = max(
                [r for r in all_results if r["success"]], key=lambda x: x["duration"]
            )

            print(f"Fastest: {fastest['duration']:.2f}s ({fastest['input']})")
            print(f"Slowest: {slowest['duration']:.2f}s ({slowest['input']})")
        else:
            self.print_colored("❌ All benchmark tests failed", "red")

        print()

    def show_help(self):
        """Show help information"""
        help_text = """
🎯 ShAI (Shae-I) Demo Script Help
================================

This demo script showcases the capabilities of ShAI, your AI-powered pickup line generator.

Available Commands:
  python demo.py                 # Run interactive demo
  python demo.py --examples      # Show example scenarios
  python demo.py --test-api      # Test Flask API endpoints
  python demo.py --benchmark     # Performance benchmark
  python demo.py --interactive   # Interactive mode (same as no args)
  python demo.py --help          # Show this help

Features Demonstrated:
✨ AI-powered pickup line generation
🎯 Situation-aware conversation starters
⚡ Fast response times
🤖 Support for both Ollama (local) and Claude API (cloud)
📱 Modern web interface integration

Setup Requirements:
• For local mode: Ollama installed and running
• For production: Claude API key configured
• Python dependencies: pip install -r requirements.txt

Configuration:
The demo respects your .env configuration:
• USE_LOCAL=true  → Uses Ollama models
• USE_LOCAL=false → Uses Claude API (requires CLAUDE_API_KEY)

Examples:
  # Quick interactive test
  python demo.py

  # See all example scenarios
  python demo.py --examples

  # Test the web API
  python demo.py --test-api

  # Performance testing
  python demo.py --benchmark

Tips:
🔧 Make sure your AI service is running before testing
🚀 Start the web app with: python app.py
💡 Try different scenarios to see varied responses
🎨 The more descriptive your input, the better the results!

Happy flirting with ShAI! 💕
"""
        print(help_text)


def main():
    """Main demo function"""
    parser = argparse.ArgumentParser(
        description="ShAI (Shae-I) Demo - AI Pickup Line Generator Showcase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--examples", action="store_true", help="Run through example scenarios"
    )
    parser.add_argument(
        "--test-api", action="store_true", help="Test Flask API endpoints"
    )
    parser.add_argument(
        "--benchmark", action="store_true", help="Run performance benchmark"
    )
    parser.add_argument(
        "--interactive", action="store_true", help="Run interactive mode (default)"
    )

    args = parser.parse_args()

    demo = ShAIDemo()
    demo.print_header()

    if args.examples:
        demo.show_configuration()
        demo.test_connectivity()
        demo.run_examples()
    elif args.test_api:
        demo.show_configuration()
        demo.test_api_endpoints()
    elif args.benchmark:
        demo.show_configuration()
        demo.test_connectivity()
        demo.benchmark_performance()
    else:
        # Default: interactive mode
        demo.show_configuration()
        demo.test_connectivity()
        demo.interactive_mode()


if __name__ == "__main__":
    main()
