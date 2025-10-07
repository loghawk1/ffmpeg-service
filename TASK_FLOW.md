# Task Processing Flow

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT REQUEST                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │    FastAPI Web Server         │
         │    (app/main.py)              │
         │    Port: $PORT                │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  POST /tasks/caption          │
         │  (app/routers/tasks.py)       │
         └───────────┬───────────────────┘
                     │
         ┌───────────┼────────────────────┐
         │           │                    │
         ▼           ▼                    ▼
    ┌────────┐  ┌────────┐        ┌─────────────┐
    │ Create │  │ Enqueue│        │   Return    │
    │ in DB  │  │ in     │        │   task_id   │
    │        │  │ Redis  │        │   to client │
    └────┬───┘  └───┬────┘        └─────────────┘
         │          │
         ▼          ▼
    ┌──────────────────────────┐
    │      SUPABASE DB         │
    │  ┌────────────────────┐  │
    │  │ tasks table        │  │
    │  │ - id (UUID)        │  │
    │  │ - status: queued   │  │
    │  │ - video_url        │  │
    │  │ - task_type        │  │
    │  └────────────────────┘  │
    └──────────────────────────┘
                 │
                 │
         ┌───────────────────────┐
         │    REDIS QUEUE        │
         │  ffmpeg:queue         │
         │  [task_id, type...]   │
         └───────┬───────────────┘
                 │
                 │ BRPOP (blocking)
                 ▼
         ┌───────────────────────────────┐
         │    Worker Process             │
         │    (worker.py)                │
         │    Running in background      │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  Dequeue Task                 │
         │  Get full task data from DB   │
         └───────────┬───────────────────┘
                     │
         ┌───────────┼────────────────────┐
         │           │                    │
         ▼           ▼                    ▼
    ┌────────┐  ┌────────┐        ┌─────────────┐
    │Caption │  │ Merge  │        │   Music     │
    │Process │  │ Process│        │   Process   │
    └────┬───┘  └───┬────┘        └─────┬───────┘
         │          │                    │
         └──────────┼────────────────────┘
                    │
                    ▼
         ┌───────────────────────────────┐
         │  Update DB Status             │
         │  - status: running            │
         │  - status: success/failed     │
         │  - result_video_url           │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  Client Polls Status          │
         │  GET /tasks/{task_id}         │
         │  Returns current status       │
         └───────────────────────────────┘
```

## Process Flow with Logging

### Step 1: Task Creation (API)
```
Client → POST /tasks/caption
  ↓
API → Validate video URL and size
  ↓
API → supabase_service.create_task()
  LOG: "Creating task with data: {...}"
  LOG: "Created task {uuid} with type caption"
  ↓
API → redis_service.enqueue_task()
  LOG: "Enqueuing task {uuid} to queue ffmpeg:queue"
  LOG: "Task {uuid} enqueued with type caption. Queue length: 1"
  ↓
API → Return 201 with task_id
```

### Step 2: Worker Processing
```
Worker → Waiting on Redis queue (BRPOP)
  LOG: "Waiting for task from queue ffmpeg:queue (timeout: 5s)"
  ↓
Worker → Task available! Dequeue
  LOG: "Dequeued task: {uuid} of type caption"
  LOG: "Task received from queue: {data}"
  ↓
Worker → process_task()
  LOG: "=========================================="
  LOG: "Starting to process task {uuid} of type caption"
  LOG: "Fetching full task data from Supabase for task {uuid}"
  LOG: "Task {uuid} data retrieved: {full_data}"
  ↓
Worker → Route to processor
  LOG: "Routing task {uuid} to caption processor"
  ↓
Processor → process_caption_task()
  LOG: "[{uuid}] Starting caption task"
  LOG: "[{uuid}] Task data: {data}"
  LOG: "[{uuid}] Updating task status to RUNNING"
  ↓
Processor → Update DB status to RUNNING
  LOG: "[{uuid}] Status updated to RUNNING"
  ↓
Processor → Download video
  LOG: "[{uuid}] Downloading video from {url}"
  ↓
Processor → Run Whisper
  LOG: "[{uuid}] Transcribing audio with Whisper model: small"
  ↓
Processor → Generate subtitles
  LOG: "[{uuid}] Generating SRT subtitles"
  ↓
Processor → Burn subtitles
  LOG: "[{uuid}] Burning subtitles into video"
  ↓
Processor → Update DB status to SUCCESS
  LOG: "[{uuid}] Caption task completed successfully"
  ↓
Worker → Task complete
  LOG: "Task {uuid} processing completed"
```

### Step 3: Client Polling
```
Client → GET /tasks/{uuid}
  LOG: "Fetching status for task {uuid}"
  ↓
API → supabase_service.get_task()
  LOG: "Querying task {uuid} from Supabase"
  LOG: "Query result for task {uuid}: data={...}"
  ↓
API → Return task status
  LOG: "Task {uuid} found with status: success"
  ↓
Client → Receives: { status: "success", video_url: "..." }
```

## Status Progression

```
queued ──────► running ──────► success
                  │                │
                  │                └──► video_url available
                  │
                  └──────► failed
                            │
                            └──► error_message available
```

## Before Fix vs After Fix

### Before (BROKEN)

```
Railway Deployment
  │
  └──► Start: python -m uvicorn app.main:app
         │
         └──► Web Server Running ✅
              │
              └──► Tasks created ✅
                   Tasks enqueued ✅

         ✗ Worker NOT running ✗
         ✗ Tasks never processed ✗
         ✗ Tasks stuck in "queued" forever ✗
```

### After (FIXED)

```
Railway Deployment
  │
  └──► Start: bash start_railway.sh
         │
         ├──► Worker Process (background) ✅
         │      │
         │      └──► Polls Redis queue
         │           Processes tasks
         │           Updates status
         │
         └──► Web Server (foreground) ✅
                │
                └──► Creates tasks
                     Enqueues tasks
                     Returns status
```

## System Components

### 1. Web Server (Foreground)
- **Process:** `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Purpose:** Handle HTTP requests
- **Endpoints:**
  - POST /tasks/* (create tasks)
  - GET /tasks/{id} (get status)
  - GET /health (health check)
  - GET /debug/queue (debug info)

### 2. Worker (Background)
- **Process:** `python worker.py`
- **Purpose:** Process tasks from queue
- **Loop:**
  - Wait for task in Redis (BRPOP)
  - Dequeue task
  - Fetch full data from Supabase
  - Route to appropriate processor
  - Update status in Supabase

### 3. Redis (Task Queue)
- **Queue:** `ffmpeg:queue`
- **Data:** `{"task_id": "uuid", "task_type": "caption"}`
- **Pattern:** LPUSH (enqueue) + BRPOP (dequeue)
- **Atomic:** Multiple workers can safely dequeue

### 4. Supabase (Task Database)
- **Table:** `tasks`
- **Primary Key:** `id` (UUID)
- **Status:** `queued` → `running` → `success`/`failed`
- **Result:** `result_video_url` or `error_message`

## Monitoring Points

### Queue Length
```bash
curl https://your-app.railway.app/debug/queue
# Returns: { "redis": { "queue_length": 0 } }
```

**Healthy:** 0-5
**Warning:** 5-20
**Critical:** >20

### Worker Heartbeat
Look for in logs:
```
Worker heartbeat - Queue length: 0
```

**Should appear:** Every 100 seconds
**If missing:** Worker crashed or hung

### Task Processing Time
```
queued → running: <5 seconds
running → success: 1-5 minutes (depends on video length)
```

### Health Status
```bash
curl https://your-app.railway.app/health
# Returns: { "status": "healthy", "redis": "connected", ... }
```

## Debug Checklist

When tasks aren't processing:

1. ✓ Check worker is running
   ```
   Look for: "Starting video processing worker..."
   ```

2. ✓ Check Redis connection
   ```
   Call: /debug/queue
   Expect: "redis": { "connected": true }
   ```

3. ✓ Check queue length
   ```
   Call: /debug/queue
   If queue_length > 0: Tasks waiting
   If queue_length = 0: Tasks completed or not created
   ```

4. ✓ Check Supabase connection
   ```
   Call: /health
   Expect: "supabase": "connected"
   ```

5. ✓ Check task exists in DB
   ```
   Call: GET /tasks/{task_id}
   Should NOT return 404
   ```

6. ✓ Check worker logs
   ```
   Look for: "Task received from queue"
   Look for: "Starting to process task"
   ```

## Success Criteria

✅ Worker process starts automatically
✅ Worker connects to Redis and Supabase
✅ Tasks are created in database
✅ Tasks are enqueued in Redis
✅ Worker dequeues and processes tasks
✅ Task status updates to "running"
✅ Task completes and status updates to "success"
✅ Client can retrieve processed video
✅ All steps are logged
✅ System state is observable via /debug endpoints
