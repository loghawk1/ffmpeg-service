#!/usr/bin/env python3
"""
Standalone test script to verify URL parsing functionality
"""
import os
from urllib.parse import urlparse, unquote


def extract_filename_from_url(url: str, default: str = "video.mp4") -> str:
    """
    Safely extract filename from URL, removing query parameters and handling edge cases
    """
    try:
        parsed_url = urlparse(url)
        path = unquote(parsed_url.path)
        filename = os.path.basename(path)

        if not filename or filename == "/":
            print(f"    ⚠️  Could not extract filename from URL")
            return default

        if not any(filename.lower().endswith(ext) for ext in ['.mp4', '.mp3', '.wav', '.mov', '.avi', '.mkv', '.webm']):
            print(f"    ⚠️  Extracted filename has unexpected extension, adding .mp4")
            filename = f"{filename}.mp4"

        # Remove invalid filesystem characters
        invalid_chars = '<>:"|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        return filename
    except Exception as e:
        print(f"    ❌ Failed to extract filename: {e}")
        return default


def test_url_parsing():
    """Test various URL formats"""

    test_cases = [
        # URL with query parameters (the problematic case)
        {
            "url": "https://dashscope-result-sh.oss-cn-shanghai.aliyuncs.com/1d/cd/20251008/bd55ff35/c758a8f7-e488-4be0-aa83-7dbbf7ef9c6f.mp4?Expires=1759943296&OSSAccessKeyId=LTAI5tKPD3TMqf2Lna1fASuh&Signature=8xfXrd5sNyx4uBPqduw1%2Bd9J7aQ%3D",
            "expected": "c758a8f7-e488-4be0-aa83-7dbbf7ef9c6f.mp4",
            "description": "URL with query parameters (Expires, OSSAccessKeyId, Signature)"
        },
        # Simple URL
        {
            "url": "https://example.com/video.mp4",
            "expected": "video.mp4",
            "description": "Simple URL without parameters"
        },
        # URL with spaces (URL encoded)
        {
            "url": "https://example.com/my%20video.mp4",
            "expected": "my video.mp4",
            "description": "URL with encoded spaces"
        },
        # URL with subdirectories
        {
            "url": "https://assets.json2video.com/clients/ie2ZO4Au3E/renders/2025-10-06-04355.mp4",
            "expected": "2025-10-06-04355.mp4",
            "description": "URL with multiple subdirectories"
        },
        # URL with fragment
        {
            "url": "https://example.com/video.mp4#start=10",
            "expected": "video.mp4",
            "description": "URL with fragment identifier"
        },
        # Audio file
        {
            "url": "https://v3.fal.media/files/koala/R9xah-zpIWdujeJVfI_Lh_output.mp3",
            "expected": "R9xah-zpIWdujeJVfI_Lh_output.mp3",
            "description": "Audio file URL"
        },
        # No extension (edge case)
        {
            "url": "https://example.com/video",
            "expected": "video.mp4",
            "description": "URL without file extension (default added)"
        },
        # WAV audio
        {
            "url": "https://v3.fal.media/files/zebra/m8xVxf5xojnXa8SB5oUnd_normalized_audio.wav",
            "expected": "m8xVxf5xojnXa8SB5oUnd_normalized_audio.wav",
            "description": "WAV audio file"
        },
    ]

    print("=" * 80)
    print("Testing URL Filename Extraction")
    print("=" * 80)
    print()

    passed = 0
    failed = 0

    for i, test in enumerate(test_cases, 1):
        url = test["url"]
        expected = test["expected"]
        description = test["description"]

        print(f"Test {i}: {description}")
        print(f"  URL: {url[:80]}{'...' if len(url) > 80 else ''}")

        result = extract_filename_from_url(url)

        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")

        if result == expected:
            print(f"  ✅ PASS")
            passed += 1
        else:
            print(f"  ❌ FAIL")
            failed += 1

        print()

    print("=" * 80)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)
    print()

    # Demonstrate the problem with os.path.basename directly
    print("=" * 80)
    print("Demonstrating the Problem with Direct os.path.basename()")
    print("=" * 80)
    print()

    problematic_url = "https://example.com/video.mp4?Expires=123&OSSAccessKeyId=ABC&Signature=xyz"

    print(f"URL: {problematic_url}")
    print()

    # Old way (problematic)
    bad_filename = os.path.basename(problematic_url)
    print(f"❌ Using os.path.basename(url) directly:")
    print(f"   Result: '{bad_filename}'")
    print(f"   Problem: Includes query parameters with invalid chars (?, &, =)")
    print()

    # New way (correct)
    good_filename = extract_filename_from_url(problematic_url)
    print(f"✅ Using extract_filename_from_url(url):")
    print(f"   Result: '{good_filename}'")
    print(f"   Solution: Clean filename without query parameters")
    print()

    print("=" * 80)

    return failed == 0


if __name__ == "__main__":
    success = test_url_parsing()
    exit(0 if success else 1)
