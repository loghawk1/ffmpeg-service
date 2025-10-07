# HOTFIX - Critical Bug Fix

## Issue
Worker was crashing immediately when trying to process tasks with error:
```
AttributeError: 'SyncSelectRequestBuilder' object has no attribute 'maybeSingle'
```

## Root Cause
The Supabase Python client uses **snake_case** method names, not **camelCase** like JavaScript:
- ❌ Wrong: `maybeSingle()`
- ✅ Correct: `maybe_single()`

## Fix Applied
**File:** `app/services/supabase_service.py`
**Line:** 99
**Change:** `maybeSingle()` → `maybe_single()`

```python
# Before (BROKEN)
result = self.client.table("tasks").select("*").eq("id", str(task_id)).maybeSingle().execute()

# After (FIXED)
result = self.client.table("tasks").select("*").eq("id", str(task_id)).maybe_single().execute()
```

## Impact
- **Before:** Worker would dequeue task from Redis but immediately crash when fetching task data
- **After:** Worker successfully fetches task data and processes tasks

## How to Verify Fix

### 1. Redeploy
Push changes and wait for Railway to redeploy.

### 2. Check Worker Logs
You should now see:
```
Task received from queue: {...}
Starting to process task {uuid} of type caption
Fetching full task data from Supabase for task {uuid}
Task {uuid} data retrieved: {...}
[{uuid}] Starting caption task
```

### 3. Test Task Processing
```bash
# Create task
curl -X POST "https://your-app.railway.app/tasks/caption" \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://example.com/video.mp4", "model_size": "small"}'

# Monitor status (should progress: queued → running → success)
curl "https://your-app.railway.app/tasks/{task_id}"
```

## Summary
This was a critical bug preventing all task processing. The fix is a simple method name correction from JavaScript-style `maybeSingle()` to Python-style `maybe_single()`.

Tasks should now process successfully end-to-end.
