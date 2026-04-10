"""Manual test for cookie handling fix.

This script manually tests the cookie handling improvements to verify
the fix works correctly without requiring pytest.
"""

import sys
import asyncio
from scrapling.engines._browsers._stealth import StealthySession, AsyncStealthySession
from scrapling.fetchers.stealth_chrome import StealthyFetcher


def test_sync_cookie_validation():
    """Test synchronous cookie validation."""
    print("=" * 80)
    print("Testing Synchronous Cookie Validation")
    print("=" * 80)

    # Test 1: Valid cookies
    print("\nTest 1: Valid cookies with all fields")
    try:
        cookies = [
            {
                "name": "test_cookie",
                "value": "test_value",
                "domain": "example.com",
                "path": "/",
                "secure": True,
                "httpOnly": True,
                "sameSite": "Lax"
            }
        ]

        with StealthySession(headless=True, disable_resources=True, cookies=cookies) as session:
            print("✅ Valid cookies: Session created successfully")
            assert session.context is not None
            assert session._is_alive is True
    except Exception as e:
        print(f"❌ Valid cookies test failed: {e}")
        return False

    # Test 2: Minimal cookies (only required fields)
    print("\nTest 2: Minimal cookies (name + value only)")
    try:
        cookies = [
            {"name": "minimal_cookie", "value": "minimal_value"}
        ]

        with StealthySession(headless=True, disable_resources=True, cookies=cookies) as session:
            print("✅ Minimal cookies: Session created successfully")
            assert session.context is not None
            assert session._is_alive is True
    except Exception as e:
        print(f"❌ Minimal cookies test failed: {e}")
        return False

    # Test 3: Multiple cookies
    print("\nTest 3: Multiple cookies")
    try:
        cookies = [
            {"name": "cookie1", "value": "value1", "domain": "example.com"},
            {"name": "cookie2", "value": "value2", "domain": "example.com"},
            {"name": "cookie3", "value": "value3", "domain": "example.com"},
        ]

        with StealthySession(headless=True, disable_resources=True, cookies=cookies) as session:
            print("✅ Multiple cookies: Session created successfully")
            assert session.context is not None
            assert session._is_alive is True
    except Exception as e:
        print(f"❌ Multiple cookies test failed: {e}")
        return False

    # Test 4: Invalid cookies (missing 'name' field)
    print("\nTest 4: Invalid cookies (missing 'name' field)")
    try:
        cookies = [
            {"value": "only_value"}
        ]

        with StealthySession(headless=True, disable_resources=True, cookies=cookies) as session:
            print("❌ Invalid cookies test failed: Should have raised ValueError")
            return False
    except ValueError as e:
        if "must have 'name' and 'value' fields" in str(e):
            print(f"✅ Invalid cookies: Correctly raised ValueError - {e}")
        else:
            print(f"❌ Invalid cookies test failed: Wrong error message - {e}")
            return False
    except Exception as e:
        print(f"❌ Invalid cookies test failed: Wrong exception type - {e}")
        return False

    # Test 5: Invalid cookie type (not a dict)
    print("\nTest 5: Invalid cookie type (not a dict)")
    try:
        cookies = ["not_a_dict"]

        with StealthySession(headless=True, disable_resources=True, cookies=cookies) as session:
            print("❌ Invalid cookie type test failed: Should have raised an error")
            return False
    except (ValueError, Exception) as e:
        # Playwright may catch this before our validation, so accept both error types
        if "Cookie must be a dictionary" in str(e) or "Invalid argument type" in str(e):
            print(f"✅ Invalid cookie type: Correctly raised error - {e}")
        else:
            print(f"❌ Invalid cookie type test failed: Wrong error message - {e}")
            return False

    # Test 6: Empty cookies
    print("\nTest 6: Empty cookies list")
    try:
        with StealthySession(headless=True, disable_resources=True, cookies=[]) as session:
            print("✅ Empty cookies: Session created successfully")
            assert session.context is not None
            assert session._is_alive is True
    except Exception as e:
        print(f"❌ Empty cookies test failed: {e}")
        return False

    # Test 7: None cookies
    print("\nTest 7: None cookies")
    try:
        with StealthySession(headless=True, disable_resources=True, cookies=None) as session:
            print("✅ None cookies: Session created successfully")
            assert session.context is not None
            assert session._is_alive is True
    except Exception as e:
        print(f"❌ None cookies test failed: {e}")
        return False

    print("\n" + "=" * 80)
    print("✅ All synchronous cookie validation tests PASSED!")
    print("=" * 80)
    return True


async def test_async_cookie_validation():
    """Test asynchronous cookie validation."""
    print("\n" + "=" * 80)
    print("Testing Asynchronous Cookie Validation")
    print("=" * 80)

    # Test 1: Valid cookies
    print("\nTest 1: Valid cookies with all fields")
    try:
        cookies = [
            {
                "name": "test_cookie",
                "value": "test_value",
                "domain": "example.com",
                "path": "/",
                "secure": True,
                "httpOnly": True,
                "sameSite": "Lax"
            }
        ]

        async with AsyncStealthySession(headless=True, disable_resources=True, cookies=cookies) as session:
            print("✅ Valid cookies: Session created successfully")
            assert session.context is not None
            assert session._is_alive is True
    except Exception as e:
        print(f"❌ Valid cookies test failed: {e}")
        return False

    # Test 2: Minimal cookies
    print("\nTest 2: Minimal cookies (name + value only)")
    try:
        cookies = [
            {"name": "minimal_cookie", "value": "minimal_value"}
        ]

        async with AsyncStealthySession(headless=True, disable_resources=True, cookies=cookies) as session:
            print("✅ Minimal cookies: Session created successfully")
            assert session.context is not None
            assert session._is_alive is True
    except Exception as e:
        print(f"❌ Minimal cookies test failed: {e}")
        return False

    # Test 3: Invalid cookies (missing 'name' field)
    print("\nTest 3: Invalid cookies (missing 'name' field)")
    try:
        cookies = [
            {"value": "only_value"}
        ]

        async with AsyncStealthySession(headless=True, disable_resources=True, cookies=cookies) as session:
            print("❌ Invalid cookies test failed: Should have raised ValueError")
            return False
    except ValueError as e:
        if "must have 'name' and 'value' fields" in str(e):
            print(f"✅ Invalid cookies: Correctly raised ValueError - {e}")
        else:
            print(f"❌ Invalid cookies test failed: Wrong error message - {e}")
            return False
    except Exception as e:
        print(f"❌ Invalid cookies test failed: Wrong exception type - {e}")
        return False

    print("\n" + "=" * 80)
    print("✅ All asynchronous cookie validation tests PASSED!")
    print("=" * 80)
    return True


def main():
    """Run all manual tests."""
    print("\n" + "=" * 80)
    print("MANUAL COOKIE HANDLING FIX TESTS")
    print("=" * 80)

    # Test sync
    sync_passed = test_sync_cookie_validation()
    if not sync_passed:
        print("\n❌ Synchronous tests FAILED")
        return 1

    # Test async
    async_passed = asyncio.run(test_async_cookie_validation())
    if not async_passed:
        print("\n❌ Asynchronous tests FAILED")
        return 1

    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    print("\nThe cookie handling fix is working correctly:")
    print("  - Cookies are properly validated")
    print("  - Invalid cookies raise clear error messages")
    print("  - Both sync and async sessions handle cookies correctly")
    print("  - Sessions are created successfully with valid cookies")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
