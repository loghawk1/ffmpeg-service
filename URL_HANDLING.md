# URL Handling and Query Parameter Support

## Overview

The FFmpeg Video Processing API now includes robust URL handling that properly supports URLs with query parameters, signed URLs, and various edge cases.

## The Problem

Many cloud storage services (AWS S3, Alibaba OSS, Google Cloud Storage, etc.) generate signed URLs with time-limited access tokens in query parameters:

```
https://storage.example.com/video.mp4?Expires=1759965331&OSSAccessKeyId=ABC123&Signature=xyz789
```

Previously, if code tried to extract filenames using `os.path.basename(url)` directly, it would include the query parameters:

```python
# ❌ INCORRECT
filename = os.path.basename(url)
# Result: "video.mp4?Expires=1759965331&OSSAccessKeyId=ABC123&Signature=xyz789"
# Problem: Contains invalid filesystem characters (?, &, =)
```

## The Solution

We've added proper URL parsing using `urllib.parse.urlparse()` to safely extract filenames:

```python
from urllib.parse import urlparse, unquote

def extract_filename_from_url(url: str, default: str = "video.mp4") -> str:
    """
    Safely extract filename from URL, removing query parameters and handling edge cases
    """
    parsed_url = urlparse(url)
    path = unquote(parsed_url.path)
    filename = os.path.basename(path)
    return filename
```

### Features

✅ **Query Parameter Removal**: Automatically strips `?key=value` parameters
✅ **URL Decoding**: Handles URL-encoded characters like `%20` (spaces)
✅ **Fragment Removal**: Strips fragments like `#section`
✅ **Invalid Character Sanitization**: Removes/replaces invalid filesystem characters
✅ **Extension Validation**: Ensures files have valid extensions
✅ **Fallback Handling**: Returns sensible defaults if extraction fails

## Current Implementation

The API already uses **task-based filenames** to avoid this issue entirely:

```python
# Caption task
video_filename = f"{task_id}_input.mp4"  # e.g., "550e8400-e29b-41d4-a716-446655440000_input.mp4"
output_filename = f"{task_id}_captioned.mp4"

# Merge task
scene_path = os.path.join(temp_dir, f"scene_{i}_video.mp4")

# Background music task
video_path = os.path.join(temp_dir, "input_video.mp4")
```

This approach:
- ✅ Avoids filename issues completely
- ✅ Ensures unique filenames per task
- ✅ Prevents filename collisions
- ✅ Makes debugging easier (task ID in filename)

## Utility Function

The `extract_filename_from_url()` function is available in `utils/file_utils.py` for any future use cases:

```python
from utils.file_utils import extract_filename_from_url

# Example usage
url = "https://storage.example.com/video.mp4?Expires=123&Signature=xyz"
filename = extract_filename_from_url(url)
# Result: "video.mp4"
```

## Error Handling for Expired URLs

The API now provides clear error messages for expired or forbidden URLs:

### 403 Forbidden Error

When a signed URL expires or requires authentication, users receive a helpful error message:

```json
{
  "detail": "Unable to access video URL: Access denied (403 Forbidden). The URL may have expired or requires authentication. Please ensure the URL is publicly accessible and not expired."
}
```

### Recommendations for Users

**For Signed URLs:**
- ✅ Generate fresh URLs with long expiration (30+ minutes)
- ✅ Ensure URL is accessible from any IP address
- ✅ Test URL in browser/curl before submitting
- ✅ Consider using permanent public URLs when possible

**Example:**
```bash
# Test URL before submitting task
curl -I "https://storage.example.com/video.mp4?Expires=123&Signature=xyz"

# Should return: HTTP/1.1 200 OK
# If returns 403, URL has expired or is not accessible
```

## Testing

A comprehensive test suite verifies URL handling:

```bash
# Run URL parsing tests
python3 test_url_parsing_standalone.py
```

### Test Cases

The test suite includes:

1. ✅ URLs with query parameters (Expires, Signature, etc.)
2. ✅ Simple URLs without parameters
3. ✅ URLs with encoded spaces (`%20`)
4. ✅ URLs with multiple subdirectories
5. ✅ URLs with fragment identifiers (`#`)
6. ✅ Audio file URLs (MP3, WAV)
7. ✅ URLs without file extensions
8. ✅ Edge cases and error conditions

### Test Results

```
================================================================================
Testing URL Filename Extraction
================================================================================

Test 1: URL with query parameters (Expires, OSSAccessKeyId, Signature)
  Expected: c758a8f7-e488-4be0-aa83-7dbbf7ef9c6f.mp4
  Got:      c758a8f7-e488-4be0-aa83-7dbbf7ef9c6f.mp4
  ✅ PASS

[... 7 more tests ...]

Results: 8 passed, 0 failed out of 8 tests
```

## Code Changes

### Modified Files

1. **`utils/file_utils.py`**
   - Added `extract_filename_from_url()` function
   - Improved error messages for 403/404 errors
   - Added URL parsing imports

2. **`API_DOCS.md`**
   - Added section on expired/forbidden URLs (403)
   - Documented signed URL handling
   - Provided examples and solutions

### New Files

1. **`test_url_parsing_standalone.py`** - Comprehensive test suite
2. **`URL_HANDLING.md`** - This documentation

## Best Practices

### For API Operators

✅ Use task-based filenames (current approach)
✅ Validate URLs before processing
✅ Provide clear error messages
✅ Log URL access failures
✅ Monitor for expired URL patterns

### For API Users

✅ Test URLs before submitting tasks
✅ Use long expiration times for signed URLs (30+ min)
✅ Consider permanent public URLs when possible
✅ Handle 403 errors gracefully in client code
✅ Implement URL refresh logic if using signed URLs

## Examples

### Valid URLs

```bash
# Simple public URL (best)
https://cdn.example.com/video.mp4

# Signed URL with long expiration (good)
https://storage.example.com/video.mp4?Expires=9999999999&Signature=abc

# URL with subdirectories (good)
https://assets.example.com/clients/user123/renders/video.mp4
```

### Problematic URLs

```bash
# ❌ Expired signed URL
https://storage.example.com/video.mp4?Expires=1234567890&Signature=abc

# ❌ IP-restricted URL
https://internal-server.local/video.mp4

# ❌ Authentication required
https://private-cdn.example.com/protected/video.mp4
```

## Summary

The API now handles URLs with query parameters correctly and provides clear error messages when URLs are inaccessible. The current implementation using task-based filenames ensures robust operation regardless of URL format.

Key improvements:
- ✅ Proper URL parsing with query parameter support
- ✅ Clear error messages for expired/forbidden URLs
- ✅ Comprehensive test coverage
- ✅ Documentation with examples
- ✅ Best practices for users
