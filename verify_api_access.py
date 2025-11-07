#!/usr/bin/env python3
"""
Quick verification script to test API connections.

This script verifies that your API tokens are working correctly.
Run this locally with your API tokens to test connectivity.

Usage:
    export APIFY_API_TOKEN=your_token
    export ANTHROPIC_API_KEY=your_key
    python verify_api_access.py
"""

import os
import json
import urllib.request
import urllib.error


def test_apify_connection():
    """Test Apify API connection."""
    token = os.getenv('APIFY_API_TOKEN')

    if not token:
        print("❌ APIFY_API_TOKEN not set")
        return False

    try:
        print("🔍 Testing Apify API connection...")

        # Test with user endpoint
        url = f"https://api.apify.com/v2/users/me?token={token}"
        req = urllib.request.Request(url)

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            username = data.get('data', {}).get('username', 'Unknown')
            print(f"✅ Apify API connected! User: {username}")
            return True

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"❌ Apify API error: {e.code} - {error_body}")
        return False
    except Exception as e:
        print(f"❌ Apify connection error: {e}")
        return False


def test_anthropic_connection():
    """Test Anthropic (Claude) API connection."""
    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        return False

    try:
        print("🔍 Testing Anthropic API connection...")

        # Simple test message
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json'
        }

        body = {
            'model': 'claude-3-5-sonnet-20241022',
            'max_tokens': 10,
            'messages': [{
                'role': 'user',
                'content': 'Say hi'
            }]
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode('utf-8'),
            headers=headers,
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            model = data.get('model', 'Unknown')
            print(f"✅ Anthropic API connected! Model: {model}")
            return True

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"❌ Anthropic API error: {e.code}")
        print(f"   {error_body}")
        return False
    except Exception as e:
        print(f"❌ Anthropic connection error: {e}")
        return False


def main():
    """Run all API verification tests."""
    print("=" * 60)
    print("  API Connection Verification")
    print("=" * 60)
    print()

    results = {
        'apify': test_apify_connection(),
        'anthropic': test_anthropic_connection()
    }

    print()
    print("=" * 60)
    print("  Results Summary")
    print("=" * 60)

    all_passed = all(results.values())

    if all_passed:
        print("✅ All API connections successful!")
        print()
        print("🚀 You're ready to run analyses!")
        print()
        print("Next steps:")
        print("  1. Add these tokens as GitHub Secrets")
        print("  2. Test with: python analyze.py --house-id test --dataset-id xyz --mock")
        print("  3. Run real analysis via GitHub Actions")
        return 0
    else:
        print("❌ Some API connections failed")
        print()
        print("Failed services:")
        for service, passed in results.items():
            if not passed:
                print(f"  • {service.upper()}")
        print()
        print("Please check your API tokens and try again.")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
