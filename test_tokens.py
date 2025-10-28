#!/usr/bin/env python3
"""
Test script to simulate token usage for the wahduh page.
This script makes API calls to generate pickup lines, which will increment the token counter.
"""

import requests
import time
import json
import random

# Configuration
BASE_URL = "http://localhost:5000"
DELAY_BETWEEN_CALLS = 2  # seconds

# Test inputs for generating pickup lines
TEST_INPUTS = [
    "coffee shop",
    "library",
    "gym",
    "beach",
    "bookstore",
    "art gallery",
    "pizza place",
    "hiking trail",
    "music festival",
    "dog park",
    "farmer's market",
    "cooking class",
    "movie theater",
    "ice cream shop",
    "park bench",
    "rainy day",
    "sunny morning",
    "late night diner",
    "airport lounge",
    "elevator",
]


def make_pickup_line_request(user_input):
    """Make a request to generate pickup lines"""
    try:
        response = requests.post(
            f"{BASE_URL}/generate",
            json={"input": user_input},
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(
                    f"✅ Generated {len(data.get('pickup_lines', []))} pickup lines for: '{user_input}'"
                )
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


def check_token_usage():
    """Check current token usage"""
    try:
        response = requests.get(f"{BASE_URL}/api/tokens", timeout=10)
        if response.status_code == 200:
            data = response.json()
            tokens = data.get("tokens", 0)
            gallons = data.get("gallons", 0.0)
            print(f"🔢 Current usage: {tokens:,} tokens = {gallons:.3f} gallons")
            return tokens, gallons
        else:
            print(f"❌ Failed to get token usage: HTTP {response.status_code}")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to check token usage: {str(e)}")
        return None, None


def main():
    """Main test function"""
    print("🚀 Starting token usage test...")
    print(f"📍 Target URL: {BASE_URL}")
    print(f"⏱️  Delay between calls: {DELAY_BETWEEN_CALLS} seconds")
    print("=" * 50)

    # Check initial token usage
    print("📊 Checking initial token usage...")
    initial_tokens, initial_gallons = check_token_usage()

    if initial_tokens is not None:
        print(
            f"🏁 Starting with: {initial_tokens:,} tokens ({initial_gallons:.3f} gallons)"
        )
    else:
        print("⚠️  Could not retrieve initial token count")

    print("\n🎯 Starting pickup line generation test...")
    print("=" * 50)

    successful_calls = 0
    failed_calls = 0

    try:
        for i, test_input in enumerate(TEST_INPUTS, 1):
            print(f"\n[{i}/{len(TEST_INPUTS)}] Testing: '{test_input}'")

            if make_pickup_line_request(test_input):
                successful_calls += 1
            else:
                failed_calls += 1

            # Check token usage every 5 calls
            if i % 5 == 0:
                print(f"\n📊 Token usage check after {i} calls:")
                check_token_usage()

            # Wait between calls (except for the last one)
            if i < len(TEST_INPUTS):
                print(f"⏳ Waiting {DELAY_BETWEEN_CALLS} seconds...")
                time.sleep(DELAY_BETWEEN_CALLS)

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user!")

    print("\n" + "=" * 50)
    print("📈 Test Results:")
    print(f"✅ Successful calls: {successful_calls}")
    print(f"❌ Failed calls: {failed_calls}")
    print(f"📊 Total calls attempted: {successful_calls + failed_calls}")

    # Check final token usage
    print("\n📊 Final token usage:")
    final_tokens, final_gallons = check_token_usage()

    if initial_tokens is not None and final_tokens is not None:
        tokens_used = final_tokens - initial_tokens
        gallons_generated = final_gallons - initial_gallons
        print(f"🎯 Tokens used in this test: {tokens_used:,}")
        print(f"⛽ Gallons generated: {gallons_generated:.3f}")

        if tokens_used > 0:
            avg_tokens_per_call = (
                tokens_used / successful_calls if successful_calls > 0 else 0
            )
            print(f"📈 Average tokens per successful call: {avg_tokens_per_call:.1f}")

    print(f"\n🌐 Visit the wahduh page to see the results: {BASE_URL}/wahduh")
    print("✨ Test completed!")


if __name__ == "__main__":
    main()
