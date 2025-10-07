# Logging and Debugging Guide

## Issue Resolved

### Problem
1. Tasks were created successfully in Supabase database
2. Tasks were enqueued in Redis successfully
3. When polling for task status (`GET /tasks/{task_id}`), the API returned "404 Task not found"
4. Tasks were never being processed (remained in "queued" status forever)

### Root Cause
**The worker process was not running!**

The Railway deployment was only starting the web server (`uvicorn app.main:app`), not the worker process (`worker.py`). Without the worker running:
- Tasks accumulated in the Redis queue
- No process was dequeuing and processing them
- The tasks existed in Supabase but were never picked up

### Solution Implemented
1. Updated `railway.json` to use a startup script
2. Created `start_railway.sh` that starts both:
   - Worker process (in background)
   - Web server (in foreground)
3. Added comprehensive logging throughout the application
4. Added `/debug/queue` endpoint for system diagnostics

## Comprehensive Logging Added

### 1. Task Creation (API)
**File:** `app/routers/tasks.py`

```python
logger.info(f"Task {task_id} created")
logger.info(f"Task {task_id} enqueued")
```

### 2. Database Operations
**File:** `app/services/supabase_service.py`

```python
logger.debug(f"Creating task with data: {task_data}")
logger.info(f"Created task {task_id} with type {task_type.value}")
logger.debug(f"Full task data: {result.data[0]}")

logger.debug(f"Querying task {task_id} from Supabase")
logger.debug(f"Query result for task {task_id}: data={result.data}")
logger.info(f"Task {task_id} retrieved successfully")
logger.warning(f"Task {task_id} not found in database")
```

### 3. Redis Queue Operations
**File:** `app/services/redis_service.py`

```python
logger.debug(f"Enqueuing task {task_id} to queue {self.queue_key}")
logger.info(f"Task {task_id} enqueued with type {task_type}. Queue length: {queue_length}")

logger.debug(f"Waiting for task from queue {self.queue_key} (timeout: {timeout}s)")
logger.info(f"Dequeued task: {task_data['task_id']} of type {task_data.get('task_type')}")
logger.debug("No task available in queue")
```

### 4. Worker Process
**File:** `worker.py`

```python
logger.info("="*60)
logger.info("Starting video processing worker...")
logger.info(f"Max concurrent workers: {settings.max_concurrent_workers}")
logger.info(f"Redis URL: {settings.redis_url}")
logger.info(f"Supabase URL: {settings.supabase_url}")
logger.info("="*60)

# Periodic heartbeat
logger.info(f"Worker heartbeat - Queue length: {queue_length}")

# Task processing
logger.info(f"Task received from queue: {task_data}")
logger.info(f"Starting to process task {task_id} of type {task_type}")
logger.info(f"Fetching full task data from Supabase for task {task_id}")
logger.info(f"Task {task_id} data retrieved: {full_task_data}")
logger.info(f"Routing task {task_id} to caption processor")
logger.info(f"Task {task_id} processing completed")
```

### 5. Task Processors
**File:** `workers/processors.py`

```python
logger.info(f"[{task_id}] Starting caption task")
logger.info(f"[{task_id}] Task data: {task_data}")
logger.info(f"[{task_id}] Updating task status to RUNNING")
logger.info(f"[{task_id}] Status updated to RUNNING")
logger.info(f"[{task_id}] Downloading video from {video_url}")
logger.info(f"[{task_id}] Transcribing audio with Whisper model: {model_size}")
logger.info(f"[{task_id}] Generating SRT subtitles")
logger.info(f"[{task_id}] Burning subtitles into video")
logger.info(f"[{task_id}] Caption task completed successfully")
logger.error(f"[{task_id}] {error_msg}", exc_info=True)
```

### 6. Task Status Retrieval
**File:** `app/routers/tasks.py`

```python
logger.info(f"Fetching status for task {task_id}")
logger.warning(f"Task {task_id} not found in database")
logger.info(f"Task {task_id} found with status: {task_data['status']}")
```

## New Debug Endpoints

### GET /debug/queue

Returns detailed system status:

```json
{
  "redis": {
    "connected": true,
    "queue_length": 0
  },
  "supabase": {
    "connected": true
  },
  "message": "Queue status retrieved"
}
```

Use this to diagnose:
- Is Redis connected?
- How many tasks are in the queue?
- Is Supabase connected?

### GET /health

Returns overall health status:

```json
{
  "status": "healthy",
  "redis": "connected",
  "supabase": "connected",
  "queue_length": 0
}
```

## How to Debug Issues

### 1. Check if Worker is Running

**In Railway logs, look for:**
```
============================================================
Starting video processing worker...
Max concurrent workers: 3
Redis URL: redis://...
Supabase URL: https://...
============================================================
Validating configuration...
Configuration validated
Connecting to Supabase...
Supabase connected
Connecting to Redis...
Redis connected
Worker connections established successfully
Starting main processing loop...
```

**If you don't see these logs, the worker is not running!**

### 2. Check Queue Status

```bash
curl https://your-app.railway.app/debug/queue
```

Expected output:
```json
{
  "redis": {
    "connected": true,
    "queue_length": 0
  },
  "supabase": {
    "connected": true
  }
}
```

If `queue_length > 0` and not decreasing, worker is not processing.

### 3. Check Task Flow

**Create a task:**
```bash
curl -X POST "https://your-app.railway.app/tasks/caption" \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://example.com/video.mp4", "model_size": "small"}'
```

**Expected logs:**
1. API creates task in Supabase
2. API enqueues task in Redis
3. Worker dequeues task
4. Worker fetches full task data
5. Worker processes task
6. Worker updates status to SUCCESS/FAILED

### 4. Monitor Worker Heartbeat

Every 100 seconds, you should see:
```
Worker heartbeat - Queue length: X
```

This confirms the worker is alive and checking the queue.

### 5. Check Task Status

```bash
curl https://your-app.railway.app/tasks/{task_id}
```

**Status progression:**
1. `queued` - Task created and waiting
2. `running` - Worker picked up the task
3. `success` - Task completed (has `video_url`)
4. `failed` - Task failed (has `error` message)

## Common Issues and Solutions

### Issue: Tasks stay in "queued" status forever

**Cause:** Worker not running

**Solution:**
1. Check Railway logs for worker startup messages
2. Verify `start_railway.sh` is being executed
3. Check for worker crash messages
4. Ensure Redis is accessible

### Issue: "Task not found" when polling

**Cause:** Multiple possibilities
1. Wrong task ID (typo)
2. Task ID not a valid UUID
3. Database connection issue

**Solution:**
1. Check the task ID carefully
2. Query database directly to verify task exists
3. Check Supabase connection in `/health`

### Issue: Worker starts but doesn't process

**Cause:** Redis connection issue

**Solution:**
1. Check `REDIS_URL` environment variable
2. Verify Redis service is running
3. Check Redis memory/connection limits
4. Look for connection errors in logs

### Issue: Tasks fail immediately

**Cause:** Various processing errors

**Solution:**
1. Check task logs: `logger.error(f"[{task_id}] ...")`
2. Common causes:
   - Video URL not accessible
   - Insufficient disk space
   - FFmpeg error
   - Whisper model not loaded
3. Check error message in task status

## Log Levels

**INFO** - Normal operations, progress updates
**DEBUG** - Detailed diagnostic information
**WARNING** - Non-critical issues
**ERROR** - Critical failures with stack traces

To enable DEBUG logging, set:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Production Monitoring

### What to Monitor

1. **Queue Length**
   - Alert if > 20 for more than 5 minutes
   - Indicates worker can't keep up

2. **Worker Heartbeat**
   - Should see heartbeat every 100s
   - Missing heartbeat = worker crashed

3. **Task Success Rate**
   - Query Supabase for failed tasks
   - Alert if failure rate > 10%

4. **Processing Time**
   - Track time from queued to completed
   - Alert if average time > 5 minutes

5. **Error Rates**
   - Count ERROR log entries
   - Alert on sudden spikes

### Recommended Tools

- **Railway Logs**: Built-in log viewer
- **Logtail**: Log aggregation and search
- **Sentry**: Error tracking and alerts
- **UptimeRobot**: Health check monitoring
- **Grafana**: Metrics and dashboards

## Testing the Fix

### 1. Restart the Service

In Railway, trigger a redeploy or restart.

### 2. Verify Worker Starts

Check logs for:
```
Starting video processing worker...
Worker connections established successfully
```

### 3. Create Test Task

```bash
TASK_ID=$(curl -X POST "https://your-app.railway.app/tasks/caption" \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://example.com/video.mp4", "model_size": "small"}' \
  | jq -r '.task_id')

echo "Task ID: $TASK_ID"
```

### 4. Monitor Processing

```bash
# Check immediately
curl "https://your-app.railway.app/tasks/$TASK_ID"
# Should show: "status": "queued"

# Wait 10 seconds
sleep 10

# Check again
curl "https://your-app.railway.app/tasks/$TASK_ID"
# Should show: "status": "running" or "success"
```

### 5. Check Worker Logs

Look for:
```
Task received from queue: ...
Starting to process task ...
Task ... processing completed
```

## Summary

The core issue was that only the web server was running, not the worker process. Tasks were created and enqueued successfully, but no worker was available to process them.

The solution:
1. Modified Railway startup to run both web + worker
2. Added extensive logging at every step
3. Added debug endpoints for diagnostics
4. Documented the complete task processing flow

With these changes, you can now:
- Verify the worker is running
- Track task progress through logs
- Debug issues quickly
- Monitor system health
