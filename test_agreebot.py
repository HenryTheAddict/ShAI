#!/usr/bin/env python3
"""
Test script for AgreeBot functionality.
This script tests the /api/agree endpoint with various inputs.
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"
DELAY_BETWEEN_TESTS = 1  # seconds

# Test inputs for AgreeBot
TEST_INPUTS = [
    "I think pineapple belongs on pizza",
    "Monday mornings are the worst",
    "Coffee is better than tea",
    "Cats are superior to dogs",
    "The sky is purple",
    "I love rainy days",
    "Homework should be illegal",
    "Ice cream for breakfast is a great idea",
    "Programming is fun",
    "The earth is flat",
    "Winter is the best season",
    "Social media is ruining society",
    "I can fly",
    "Chocolate solves everything",
    "Working from home is amazing",
    "Aliens definitely exist",
    "I'm the smartest person alive",
    "Money doesn't buy happiness",
    "Books are better than movies",
    "I should quit my job and become a professional unicorn trainer",
]


def test_agreebot_api(user_input):
    """Test the AgreeBot API with a given input"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/agree",
            json={"input": user_input},
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                agreements = data.get("agreements", [])
                print(f"✅ Input: '{user_input}'")
                print(f"   AgreeBot generated {len(agreements)} agreements:")
                for i, agreement in enumerate(agreements, 1):
                    print(f"   {i}. {agreement}")
                print()
                return True
            else:
                print(
                    f"❌ API returned error for '{user_input}': {data.get('error', 'Unknown error')}"
                )
                return False
        else:
            print(f"❌ HTTP {response.status_code} for '{user_input}': {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed for '{user_input}': {str(e)}")
        return False


def test_edge_cases():
    """Test edge cases for AgreeBot"""
    print("🧪 Testing Edge Cases:")
    print("=" * 50)

    edge_cases = [
        "",  # Empty input
        "   ",  # Whitespace only
        "a" * 1000,  # Very long input
        "!@#$%^&*()",  # Special characters only
        "123456789",  # Numbers only
        "I hate everything and everyone including myself",  # Very negative
        "AgreeBot is stupid and wrong",  # Insulting AgreeBot itself
    ]

    for case in edge_cases:
        print(f"\nTesting: '{case[:50]}{'...' if len(case) > 50 else ''}'")
        test_agreebot_api(case)
        time.sleep(0.5)


def main():
    """Main test function"""
    print("🤖 Starting AgreeBot API tests...")
    print(f"📍 Target URL: {BASE_URL}")
    print("=" * 60)

    # Test if the server is running
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Server is running!")
        else:
            print("⚠️  Server might have issues, but continuing with tests...")
    except:
        print("❌ Cannot connect to server. Make sure it's running on localhost:5000")
        return

    print("\n🎯 Testing AgreeBot with various inputs...")
    print("=" * 60)

    successful_tests = 0
    failed_tests = 0

    try:
        for i, test_input in enumerate(TEST_INPUTS, 1):
            print(f"[Test {i}/{len(TEST_INPUTS)}]")

            if test_agreebot_api(test_input):
                successful_tests += 1
            else:
                failed_tests += 1

            if i < len(TEST_INPUTS):
                time.sleep(DELAY_BETWEEN_TESTS)

        # Test edge cases
        print("\n" + "=" * 60)
        test_edge_cases()

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user!")

    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"✅ Successful tests: {successful_tests}")
    print(f"❌ Failed tests: {failed_tests}")
    print(f"📈 Total tests: {successful_tests + failed_tests}")

    if successful_tests > 0:
        success_rate = (successful_tests / (successful_tests + failed_tests)) * 100
        print(f"🎯 Success rate: {success_rate:.1f}%")

    print(f"\n🌐 Visit AgreeBot in your browser: {BASE_URL}/agreebot")
    print("✨ AgreeBot testing completed!")
    print("\n💡 Remember: AgreeBot should agree with EVERYTHING!")


if __name__ == "__main__":
    main()
