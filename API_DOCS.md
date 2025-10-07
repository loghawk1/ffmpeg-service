# FFmpeg Video Processing API Documentation

**Version:** 1.0.0
**Last Updated:** October 7, 2025
**Base URL:** `https://fantastic-endurance-production.up.railway.app`

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Base URL](#base-url)
4. [API Endpoints](#api-endpoints)
   - [Submit Caption Task](#submit-caption-task)
   - [Submit Merge Task](#submit-merge-task)
   - [Submit Background Music Task](#submit-background-music-task)
   - [Get Task Status](#get-task-status)
   - [Download Video](#download-video)
   - [Health Check](#health-check)
   - [Debug Queue Status](#debug-queue-status)
5. [Request/Response Models](#requestresponse-models)
6. [Task Lifecycle](#task-lifecycle)
7. [Status Codes and Error Handling](#status-codes-and-error-handling)
8. [Code Examples](#code-examples)
9. [Rate Limits and Constraints](#rate-limits-and-constraints)
10. [Configuration](#configuration)
11. [Security](#security)
12. [Troubleshooting](#troubleshooting)
13. [Interactive Documentation](#interactive-documentation)

---

## Overview

The FFmpeg Video Processing API is a production-ready asynchronous microservice for video processing operations. It provides three main capabilities:

### Core Features

- **Video Captioning**: Add AI-generated subtitles to videos using OpenAI Whisper
- **Video Merging**: Combine multiple video scenes with voiceovers into a single video
- **Background Music**: Add background music to videos with volume control

### Key Characteristics

- **Asynchronous Processing**: Submit tasks and poll for completion
- **REST API**: Simple HTTP endpoints with JSON payloads
- **File Size Limits**: 100MB per file with configurable limits
- **Automatic Cleanup**: Processed videos expire after 2 hours
- **Health Monitoring**: Built-in health checks and queue metrics
- **Format Support**: MP4, MOV, AVI for video; MP3, WAV, AAC for audio

### Architecture

The API uses a two-process architecture:
- **Web Server**: Handles HTTP requests and task submission
- **Worker Process**: Processes video tasks asynchronously using Redis queue
- **Supabase**: Stores task metadata and status
- **Redis**: Task queue and job coordination

---

## Quick Start

### 1. Submit a Caption Task

```bash
curl -X POST "https://fantastic-endurance-production.up.railway.app/tasks/caption" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://example.com/video.mp4",
    "model_size": "small"
  }'
```

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Caption task queued successfully"
}
```

### 2. Poll for Task Status

```bash
curl "https://fantastic-endurance-production.up.railway.app/tasks/550e8400-e29b-41d4-a716-446655440000"
```

**Response (Processing):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "video_url": null,
  "error": null,
  "created_at": "2025-10-07T12:00:00Z",
  "updated_at": "2025-10-07T12:01:00Z",
  "completed_at": null
}
```

**Response (Complete):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "success",
  "video_url": "https://fantastic-endurance-production.up.railway.app/video/550e8400-e29b-41d4-a716-446655440000_captioned.mp4",
  "error": null,
  "created_at": "2025-10-07T12:00:00Z",
  "updated_at": "2025-10-07T12:05:00Z",
  "completed_at": "2025-10-07T12:05:00Z"
}
```

### 3. Download the Processed Video

```bash
curl "https://fantastic-endurance-production.up.railway.app/video/550e8400-e29b-41d4-a716-446655440000_captioned.mp4" \
  -o captioned_video.mp4
```

---

## Base URL

**Production API:** `https://fantastic-endurance-production.up.railway.app`

All endpoints are relative to this base URL.

**Example Endpoints:**
- Caption submission: `https://fantastic-endurance-production.up.railway.app/tasks/caption`
- Task status: `https://fantastic-endurance-production.up.railway.app/tasks/{task_id}`
- Video download: `https://fantastic-endurance-production.up.railway.app/video/{filename}`
- Health check: `https://fantastic-endurance-production.up.railway.app/health`

---

## API Endpoints

### Submit Caption Task

Add AI-generated subtitles to a video using OpenAI Whisper.

**Endpoint:** `POST /tasks/caption`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "video_url": "https://example.com/video.mp4",
  "model_size": "small"
}
```

**Parameters:**

| Parameter | Type | Required | Description | Valid Values |
|-----------|------|----------|-------------|--------------|
| video_url | string (URL) | Yes | URL of the video to process | Must be publicly accessible HTTP/HTTPS URL |
| model_size | string | No | Whisper model size | `tiny`, `base`, `small` (default), `medium`, `large` |

**Model Size Characteristics:**

- `tiny`: Fastest, least accurate, ~75MB
- `base`: Fast, good for simple speech, ~140MB
- `small`: Balanced (default), ~465MB
- `medium`: Higher accuracy, slower, ~1.5GB
- `large`: Best accuracy, slowest, ~2.9GB

**Response:** `201 Created`
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Caption task queued successfully"
}
```

**Processing Details:**
- Transcribes audio using Whisper
- Generates SRT subtitles with max 3 words per line
- Burns subtitles into video with white text and black outline
- Output filename: `{task_id}_captioned.mp4`
- Average processing time: 1-5 minutes depending on video length and model size

**Complete Example with Real Video:**

```bash
# Submit caption task
curl -X POST "https://fantastic-endurance-production.up.railway.app/tasks/caption" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://assets.json2video.com/clients/ie2ZO4Au3E/renders/2025-10-06-04355.mp4",
    "model_size": "small"
  }'
```

**Expected Response:**
```json
{
  "task_id": "a7f2e8c9-3b1d-4a6e-9c7f-8d2e5b4a1c3d",
  "status": "queued",
  "message": "Caption task queued successfully"
}
```

**Poll Status (after 30 seconds):**
```bash
curl "https://fantastic-endurance-production.up.railway.app/tasks/a7f2e8c9-3b1d-4a6e-9c7f-8d2e5b4a1c3d"
```

**Response (Running):**
```json
{
  "task_id": "a7f2e8c9-3b1d-4a6e-9c7f-8d2e5b4a1c3d",
  "status": "running",
  "video_url": null,
  "error": null,
  "created_at": "2025-10-07T15:30:00.000Z",
  "updated_at": "2025-10-07T15:30:15.000Z",
  "completed_at": null
}
```

**Poll Status (after 3 minutes):**
```json
{
  "task_id": "a7f2e8c9-3b1d-4a6e-9c7f-8d2e5b4a1c3d",
  "status": "success",
  "video_url": "https://fantastic-endurance-production.up.railway.app/video/a7f2e8c9-3b1d-4a6e-9c7f-8d2e5b4a1c3d_captioned.mp4",
  "error": null,
  "created_at": "2025-10-07T15:30:00.000Z",
  "updated_at": "2025-10-07T15:33:45.000Z",
  "completed_at": "2025-10-07T15:33:45.000Z"
}
```

**Download Result:**
```bash
curl "https://fantastic-endurance-production.up.railway.app/video/a7f2e8c9-3b1d-4a6e-9c7f-8d2e5b4a1c3d_captioned.mp4" \
  -o my_captioned_video.mp4
```

---

### Submit Merge Task

Combine multiple video scenes with voiceovers into a single video.

**Endpoint:** `POST /tasks/merge`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "scene_clip_urls": [
    "https://example.com/scene1.mp4",
    "https://example.com/scene2.mp4"
  ],
  "voiceover_urls": [
    "https://example.com/voice1.mp3",
    "https://example.com/voice2.mp3"
  ],
  "width": 1080,
  "height": 1920,
  "video_volume": 0.2,
  "voiceover_volume": 2.0
}
```

**Parameters:**

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| scene_clip_urls | array[string] | Yes | List of scene video URLs | Min: 1 scene, must match voiceover count |
| voiceover_urls | array[string] | Yes | List of voiceover audio URLs | Min: 1 audio, must match scene count |
| width | integer | No | Output video width in pixels | Range: 480-3840, default: 1080 |
| height | integer | No | Output video height in pixels | Range: 480-3840, default: 1920 |
| video_volume | float | No | Volume level for video audio | Range: 0.0-1.0, default: 0.2 |
| voiceover_volume | float | No | Volume level for voiceover | Range: 0.0-10.0, default: 2.0 |

**Response:** `201 Created`
```json
{
  "task_id": "660f9511-f39c-52e5-b827-557766551111",
  "status": "queued",
  "message": "Merge task queued successfully"
}
```

**Processing Details:**
- Downloads all scenes and voiceovers in parallel
- Scales/crops each video to target dimensions using cover mode
- Mixes video audio with corresponding voiceover
- Concatenates all processed scenes sequentially
- Output filename: `{task_id}_merged.mp4`
- Average processing time: 2-10 minutes depending on scene count
- Total file size limit: 500MB (100MB × 5)

**Complete Example with Real Videos:**

```bash
# Submit merge task
curl -X POST "https://fantastic-endurance-production.up.railway.app/tasks/merge" \
  -H "Content-Type: application/json" \
  -d '{
    "scene_clip_urls": [
      "https://dashscope-result-sh.oss-cn-shanghai.aliyuncs.com/1d/ec/20251006/621d405c/d4ca0899-3ae0-4e39-a1ad-72c566cb523e.mp4",
      "https://dashscope-result-sh.oss-cn-shanghai.aliyuncs.com/1d/95/20251006/bd55ff35/f8136329-edf4-42ef-b2f9-41e6c150bc89.mp4"
    ],
    "voiceover_urls": [
      "https://v3.fal.media/files/koala/R9xah-zpIWdujeJVfI_Lh_output.mp3",
      "https://v3.fal.media/files/rabbit/0UNjgXiomqsqpRwtebRTj_output.mp3"
    ],
    "width": 1080,
    "height": 1920,
    "video_volume": 0.2,
    "voiceover_volume": 2.0
  }'
```

**Expected Response:**
```json
{
  "task_id": "b4e9f7a2-8c3d-4e1f-a6b9-5d8c7e2f1a4b",
  "status": "queued",
  "message": "Merge task queued successfully"
}
```

**Poll Status Throughout Process:**

**After 1 minute (Queued):**
```json
{
  "task_id": "b4e9f7a2-8c3d-4e1f-a6b9-5d8c7e2f1a4b",
  "status": "queued",
  "video_url": null,
  "error": null,
  "created_at": "2025-10-07T16:00:00.000Z",
  "updated_at": "2025-10-07T16:00:00.000Z",
  "completed_at": null
}
```

**After 2 minutes (Running):**
```json
{
  "task_id": "b4e9f7a2-8c3d-4e1f-a6b9-5d8c7e2f1a4b",
  "status": "running",
  "video_url": null,
  "error": null,
  "created_at": "2025-10-07T16:00:00.000Z",
  "updated_at": "2025-10-07T16:01:30.000Z",
  "completed_at": null
}
```

**After 6 minutes (Success):**
```json
{
  "task_id": "b4e9f7a2-8c3d-4e1f-a6b9-5d8c7e2f1a4b",
  "status": "success",
  "video_url": "https://fantastic-endurance-production.up.railway.app/video/b4e9f7a2-8c3d-4e1f-a6b9-5d8c7e2f1a4b_merged.mp4",
  "error": null,
  "created_at": "2025-10-07T16:00:00.000Z",
  "updated_at": "2025-10-07T16:06:20.000Z",
  "completed_at": "2025-10-07T16:06:20.000Z"
}
```

**Download Result:**
```bash
curl "https://fantastic-endurance-production.up.railway.app/video/b4e9f7a2-8c3d-4e1f-a6b9-5d8c7e2f1a4b_merged.mp4" \
  -o merged_video.mp4
```

---

### Submit Background Music Task

Add background music to a video with volume control.

**Endpoint:** `POST /tasks/background-music`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "video_url": "https://example.com/video.mp4",
  "music_url": "https://example.com/music.mp3",
  "music_volume": 0.3,
  "video_volume": 1.0
}
```

**Parameters:**

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| video_url | string (URL) | Yes | URL of the video to process | Must be publicly accessible |
| music_url | string (URL) | Yes | URL of the background music file | MP3, WAV, AAC supported |
| music_volume | float | No | Volume level for background music | Range: 0.0-1.0, default: 0.3 |
| video_volume | float | No | Volume level for video audio | Range: 0.0-1.0, default: 1.0 |

**Response:** `201 Created`
```json
{
  "task_id": "770fa622-g4ad-63f6-c938-668877662222",
  "status": "queued",
  "message": "Background music task queued successfully"
}
```

**Processing Details:**
- Detects video duration using FFprobe
- Loops background music to match video duration
- Mixes audio streams with specified volumes
- Copies video stream without re-encoding (fast)
- Output filename: `{task_id}_with_music.mp4`
- Average processing time: 30 seconds to 2 minutes
- Total file size limit: 200MB (100MB × 2)

**Complete Example with Real Files:**

```bash
# Submit background music task
curl -X POST "https://fantastic-endurance-production.up.railway.app/tasks/background-music" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://assets.json2video.com/clients/ie2ZO4Au3E/renders/2025-10-06-26438.mp4",
    "music_url": "https://v3.fal.media/files/zebra/m8xVxf5xojnXa8SB5oUnd_normalized_audio.wav",
    "music_volume": 0.3,
    "video_volume": 1.0
  }'
```

**Expected Response:**
```json
{
  "task_id": "c9d8e7f6-2a1b-4c3d-8e7f-6a5b4c3d2e1f",
  "status": "queued",
  "message": "Background music task queued successfully"
}
```

**Poll Status:**

**After 30 seconds (Running):**
```json
{
  "task_id": "c9d8e7f6-2a1b-4c3d-8e7f-6a5b4c3d2e1f",
  "status": "running",
  "video_url": null,
  "error": null,
  "created_at": "2025-10-07T17:00:00.000Z",
  "updated_at": "2025-10-07T17:00:20.000Z",
  "completed_at": null
}
```

**After 1.5 minutes (Success):**
```json
{
  "task_id": "c9d8e7f6-2a1b-4c3d-8e7f-6a5b4c3d2e1f",
  "status": "success",
  "video_url": "https://fantastic-endurance-production.up.railway.app/video/c9d8e7f6-2a1b-4c3d-8e7f-6a5b4c3d2e1f_with_music.mp4",
  "error": null,
  "created_at": "2025-10-07T17:00:00.000Z",
  "updated_at": "2025-10-07T17:01:35.000Z",
  "completed_at": "2025-10-07T17:01:35.000Z"
}
```

**Download Result:**
```bash
curl "https://fantastic-endurance-production.up.railway.app/video/c9d8e7f6-2a1b-4c3d-8e7f-6a5b4c3d2e1f_with_music.mp4" \
  -o video_with_music.mp4
```

---

### Get Task Status

Poll the status of a submitted task.

**Endpoint:** `GET /tasks/{task_id}`

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| task_id | UUID | The task ID returned from task submission |

**Example Request:**
```bash
curl "https://fantastic-endurance-production.up.railway.app/tasks/550e8400-e29b-41d4-a716-446655440000"
```

**Response:** `200 OK`
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "success",
  "video_url": "https://fantastic-endurance-production.up.railway.app/video/550e8400-e29b-41d4-a716-446655440000_captioned.mp4",
  "error": null,
  "created_at": "2025-10-07T12:00:00Z",
  "updated_at": "2025-10-07T12:05:00Z",
  "completed_at": "2025-10-07T12:05:00Z"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| task_id | UUID | Unique task identifier |
| status | string | Current status: `queued`, `running`, `success`, `failed` |
| video_url | string \| null | Public URL of processed video (only when status is `success`) |
| error | string \| null | Error message (only when status is `failed`) |
| created_at | timestamp | When task was created |
| updated_at | timestamp | Last status update time |
| completed_at | timestamp \| null | When task completed (success or failed) |

**Status Progression Example:**

**Immediately after submission (Queued):**
```json
{
  "task_id": "d5e4f3a2-1b0c-9d8e-7f6a-5b4c3d2e1f0a",
  "status": "queued",
  "video_url": null,
  "error": null,
  "created_at": "2025-10-07T18:00:00.000Z",
  "updated_at": "2025-10-07T18:00:00.000Z",
  "completed_at": null
}
```

**Worker picks up task (Running):**
```json
{
  "task_id": "d5e4f3a2-1b0c-9d8e-7f6a-5b4c3d2e1f0a",
  "status": "running",
  "video_url": null,
  "error": null,
  "created_at": "2025-10-07T18:00:00.000Z",
  "updated_at": "2025-10-07T18:00:45.000Z",
  "completed_at": null
}
```

**Processing complete (Success):**
```json
{
  "task_id": "d5e4f3a2-1b0c-9d8e-7f6a-5b4c3d2e1f0a",
  "status": "success",
  "video_url": "https://fantastic-endurance-production.up.railway.app/video/d5e4f3a2-1b0c-9d8e-7f6a-5b4c3d2e1f0a_captioned.mp4",
  "error": null,
  "created_at": "2025-10-07T18:00:00.000Z",
  "updated_at": "2025-10-07T18:03:22.000Z",
  "completed_at": "2025-10-07T18:03:22.000Z"
}
```

**Processing failed (Failed):**
```json
{
  "task_id": "e6f5a4b3-2c1d-0e9f-8a7b-6c5d4e3f2a1b",
  "status": "failed",
  "video_url": null,
  "error": "FFmpeg processing failed: Invalid video codec",
  "created_at": "2025-10-07T18:10:00.000Z",
  "updated_at": "2025-10-07T18:11:15.000Z",
  "completed_at": "2025-10-07T18:11:15.000Z"
}
```

**Polling Recommendations:**
- Poll every 5 seconds for optimal balance
- Exponential backoff recommended for long-running tasks
- Stop polling once status is `success` or `failed`
- Tasks typically complete in 1-10 minutes

---

### Download Video

Download or stream a processed video file.

**Endpoint:** `GET /video/{filename}`

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| filename | string | Video filename from task status response |

**Filename Patterns:**
- Caption: `{task_id}_captioned.mp4`
- Merge: `{task_id}_merged.mp4`
- Background Music: `{task_id}_with_music.mp4`

**Example Request:**
```bash
curl "https://fantastic-endurance-production.up.railway.app/video/550e8400-e29b-41d4-a716-446655440000_captioned.mp4" \
  -o output.mp4
```

**Response:** `200 OK`

**Response Headers:**
```
Content-Type: video/mp4
Content-Length: 15728640
Content-Disposition: inline; filename="550e8400-e29b-41d4-a716-446655440000_captioned.mp4"
Cache-Control: public, max-age=3600
Accept-Ranges: bytes
```

**Features:**
- Supports HTTP Range requests for streaming
- Includes cache headers (1 hour)
- Can be embedded in video players
- Direct download supported

**Browser Streaming Example:**
```html
<!DOCTYPE html>
<html>
<body>
  <video controls width="640" height="360">
    <source
      src="https://fantastic-endurance-production.up.railway.app/video/550e8400-e29b-41d4-a716-446655440000_captioned.mp4"
      type="video/mp4">
    Your browser does not support the video tag.
  </video>
</body>
</html>
```

**Range Request Example (Streaming first 1MB):**
```bash
curl "https://fantastic-endurance-production.up.railway.app/video/550e8400-e29b-41d4-a716-446655440000_captioned.mp4" \
  -H "Range: bytes=0-1048576" \
  -o partial_video.mp4
```

**Download with Progress:**
```bash
curl "https://fantastic-endurance-production.up.railway.app/video/550e8400-e29b-41d4-a716-446655440000_captioned.mp4" \
  --progress-bar \
  -o downloaded_video.mp4
```

---

### Health Check

Check the health status of the API and its dependencies.

**Endpoint:** `GET /health`

**Example Request:**
```bash
curl "https://fantastic-endurance-production.up.railway.app/health"
```

**Response (Healthy):** `200 OK`
```json
{
  "status": "healthy",
  "redis": "connected",
  "supabase": "connected",
  "queue_length": 3
}
```

**Response (Degraded):** `200 OK`
```json
{
  "status": "degraded",
  "redis": "disconnected",
  "supabase": "connected",
  "queue_length": 0
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| status | string | Overall health: `healthy` or `degraded` |
| redis | string | Redis connection status: `connected` or `disconnected` |
| supabase | string | Supabase connection status: `connected` or `disconnected` |
| queue_length | integer | Number of tasks currently in queue |

**Status Interpretations:**
- `healthy`: All services connected, API fully operational
- `degraded`: One or more services disconnected, limited functionality

**Use Cases:**
- Load balancer health checks
- Monitoring and alerting
- System diagnostics
- Pre-deployment verification

---

### Debug Queue Status

Get detailed queue and system status for debugging.

**Endpoint:** `GET /debug/queue`

**Example Request:**
```bash
curl "https://fantastic-endurance-production.up.railway.app/debug/queue"
```

**Response:** `200 OK`
```json
{
  "redis": {
    "connected": true,
    "queue_length": 5
  },
  "supabase": {
    "connected": true
  },
  "message": "Queue status retrieved"
}
```

**Response (With Issues):**
```json
{
  "redis": {
    "connected": false,
    "queue_length": 0
  },
  "supabase": {
    "connected": true
  },
  "message": "Queue status retrieved"
}
```

**Use Cases:**
- Troubleshooting task processing issues
- Monitoring queue backlog
- Verifying service connections
- Debugging worker problems

---

## Request/Response Models

### CaptionTaskRequest

```json
{
  "video_url": "https://example.com/video.mp4",
  "model_size": "small"
}
```

**Schema:**
```typescript
{
  video_url: string (URL, required)
  model_size: "tiny" | "base" | "small" | "medium" | "large" (optional, default: "small")
}
```

**Validation Rules:**
- `video_url` must be a valid HTTP/HTTPS URL
- `video_url` must be publicly accessible
- File at URL must be ≤100MB
- `model_size` must be one of the valid options

**Example Variations:**

**Minimal request (uses defaults):**
```json
{
  "video_url": "https://example.com/video.mp4"
}
```

**With tiny model (fastest):**
```json
{
  "video_url": "https://example.com/video.mp4",
  "model_size": "tiny"
}
```

**With large model (best quality):**
```json
{
  "video_url": "https://example.com/video.mp4",
  "model_size": "large"
}
```

---

### MergeTaskRequest

```json
{
  "scene_clip_urls": ["https://example.com/scene1.mp4", "https://example.com/scene2.mp4"],
  "voiceover_urls": ["https://example.com/voice1.mp3", "https://example.com/voice2.mp3"],
  "width": 1080,
  "height": 1920,
  "video_volume": 0.2,
  "voiceover_volume": 2.0
}
```

**Schema:**
```typescript
{
  scene_clip_urls: string[] (required, min_length: 1)
  voiceover_urls: string[] (required, min_length: 1)
  width: integer (optional, range: 480-3840, default: 1080)
  height: integer (optional, range: 480-3840, default: 1920)
  video_volume: float (optional, range: 0.0-1.0, default: 0.2)
  voiceover_volume: float (optional, range: 0.0-10.0, default: 2.0)
}
```

**Validation Rules:**
- Array lengths must match: `scene_clip_urls.length === voiceover_urls.length`
- Each URL must be publicly accessible
- Total combined file size must be ≤500MB
- Dimensions must be within valid range

**Example Variations:**

**Minimal (3 scenes with defaults):**
```json
{
  "scene_clip_urls": [
    "https://example.com/scene1.mp4",
    "https://example.com/scene2.mp4",
    "https://example.com/scene3.mp4"
  ],
  "voiceover_urls": [
    "https://example.com/voice1.mp3",
    "https://example.com/voice2.mp3",
    "https://example.com/voice3.mp3"
  ]
}
```

**Landscape video (1920×1080):**
```json
{
  "scene_clip_urls": ["https://example.com/scene1.mp4"],
  "voiceover_urls": ["https://example.com/voice1.mp3"],
  "width": 1920,
  "height": 1080
}
```

**Silent video background (no video audio):**
```json
{
  "scene_clip_urls": ["https://example.com/scene1.mp4"],
  "voiceover_urls": ["https://example.com/voice1.mp3"],
  "video_volume": 0.0,
  "voiceover_volume": 2.5
}
```

---

### BackgroundMusicTaskRequest

```json
{
  "video_url": "https://example.com/video.mp4",
  "music_url": "https://example.com/music.mp3",
  "music_volume": 0.3,
  "video_volume": 1.0
}
```

**Schema:**
```typescript
{
  video_url: string (URL, required)
  music_url: string (URL, required)
  music_volume: float (optional, range: 0.0-1.0, default: 0.3)
  video_volume: float (optional, range: 0.0-1.0, default: 1.0)
}
```

**Validation Rules:**
- Both URLs must be publicly accessible
- Total combined file size must be ≤200MB
- Volumes must be within valid ranges

**Example Variations:**

**Minimal (uses defaults):**
```json
{
  "video_url": "https://example.com/video.mp4",
  "music_url": "https://example.com/music.mp3"
}
```

**Louder background music:**
```json
{
  "video_url": "https://example.com/video.mp4",
  "music_url": "https://example.com/music.mp3",
  "music_volume": 0.6,
  "video_volume": 0.8
}
```

**Quiet background music:**
```json
{
  "video_url": "https://example.com/video.mp4",
  "music_url": "https://example.com/music.mp3",
  "music_volume": 0.15,
  "video_volume": 1.0
}
```

---

### TaskResponse

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Caption task queued successfully"
}
```

**Schema:**
```typescript
{
  task_id: UUID (string)
  status: "queued" | "running" | "success" | "failed"
  message: string
}
```

**Example Messages:**
- Caption: `"Caption task queued successfully"`
- Merge: `"Merge task queued successfully"`
- Background Music: `"Background music task queued successfully"`

---

### TaskStatusResponse

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "success",
  "video_url": "https://fantastic-endurance-production.up.railway.app/video/550e8400-..._captioned.mp4",
  "error": null,
  "created_at": "2025-10-07T12:00:00Z",
  "updated_at": "2025-10-07T12:05:00Z",
  "completed_at": "2025-10-07T12:05:00Z"
}
```

**Schema:**
```typescript
{
  task_id: UUID (string)
  status: "queued" | "running" | "success" | "failed"
  video_url: string | null
  error: string | null
  created_at: timestamp (ISO 8601)
  updated_at: timestamp (ISO 8601)
  completed_at: timestamp | null (ISO 8601)
}
```

---

### HealthCheckResponse

```json
{
  "status": "healthy",
  "redis": "connected",
  "supabase": "connected",
  "queue_length": 5
}
```

**Schema:**
```typescript
{
  status: "healthy" | "degraded"
  redis: "connected" | "disconnected"
  supabase: "connected" | "disconnected"
  queue_length: integer
}
```

---

## Task Lifecycle

### State Diagram

```
┌─────────┐
│ queued  │ ──────┐
└─────────┘       │
                  ▼
            ┌──────────┐
            │ running  │
            └──────────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
    ┌─────────┐      ┌─────────┐
    │ success │      │ failed  │
    └─────────┘      └─────────┘
```

### Status Transitions

**1. queued → running**
- Worker picks up task from Redis queue
- Task status updated in Supabase
- Processing begins immediately
- Average wait time: 0-30 seconds (depending on queue)

**2. running → success**
- Task completes successfully
- Video saved to disk
- `video_url` field populated
- `completed_at` timestamp set
- Video available for 2 hours

**3. running → failed**
- Error occurs during processing
- `error` field contains error message
- `completed_at` timestamp set
- Partial files cleaned up automatically

### Timing Expectations

| Task Type | Typical Duration | Variables |
|-----------|------------------|-----------|
| Caption (tiny model) | 30 sec - 1 min | Video length |
| Caption (small model) | 1-3 minutes | Video length, audio complexity |
| Caption (large model) | 3-8 minutes | Video length, audio complexity |
| Merge (2 scenes) | 2-5 minutes | Scene count, dimensions, file sizes |
| Merge (5 scenes) | 5-12 minutes | Scene count, dimensions, file sizes |
| Background Music | 30 seconds - 2 minutes | Video length, audio length |

### Real-World Timing Example

**Caption Task (5-minute video, small model):**
```
00:00 - Task submitted (status: queued)
00:15 - Worker picks up task (status: running)
00:20 - Downloading video
01:30 - Running Whisper transcription
03:00 - Generating SRT file
03:15 - Burning subtitles with FFmpeg
04:45 - Uploading result
05:00 - Task complete (status: success)
```

**Merge Task (3 scenes):**
```
00:00 - Task submitted (status: queued)
00:10 - Worker picks up task (status: running)
00:15 - Downloading all videos and audio in parallel
01:45 - Processing scene 1 (scale, mix audio)
03:30 - Processing scene 2
05:15 - Processing scene 3
06:00 - Concatenating all scenes
07:30 - Task complete (status: success)
```

### Video Expiration

- Processed videos expire **2 hours** after completion
- Automatic cleanup runs every hour
- Download videos before expiration
- No extension available - resubmit task if needed

**Expiration Timeline:**
```
Task completed at: 2025-10-07 15:00:00
Video available until: 2025-10-07 17:00:00
Cleanup runs at: 2025-10-07 17:00:00
Video deleted by: 2025-10-07 17:05:00
```

---

## Status Codes and Error Handling

### HTTP Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Task created successfully |
| 400 | Bad Request | Invalid request parameters |
| 404 | Not Found | Task or video not found |
| 413 | Payload Too Large | File exceeds size limit |
| 500 | Internal Server Error | Server error occurred |

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Scenarios

#### 1. File Too Large (413)

**Request:**
```bash
curl -X POST "https://fantastic-endurance-production.up.railway.app/tasks/caption" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://example.com/huge-video-150mb.mp4",
    "model_size": "small"
  }'
```

**Response:**
```json
{
  "detail": "File size 150.5MB exceeds limit of 100MB"
}
```

**Solution:**
- Compress video before uploading
- Reduce resolution or bitrate
- Split large videos into segments
- Contact admin to increase MAX_FILE_SIZE_MB

---

#### 2. Invalid URL (400)

**Request:**
```bash
curl -X POST "https://fantastic-endurance-production.up.railway.app/tasks/caption" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://example.com/nonexistent-video.mp4",
    "model_size": "small"
  }'
```

**Response:**
```json
{
  "detail": "Unable to access video URL: HTTP error 404"
}
```

**Solution:**
- Verify URL is correct and accessible
- Check URL returns 200 OK status
- Ensure URL doesn't require authentication
- Test URL in browser first

---

#### 3. Unreachable URL (400)

**Request:**
```bash
curl -X POST "https://fantastic-endurance-production.up.railway.app/tasks/caption" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://internal-server.local/video.mp4",
    "model_size": "small"
  }'
```

**Response:**
```json
{
  "detail": "Unable to access video URL: Connection timeout"
}
```

**Solution:**
- Ensure URL is publicly accessible
- Check firewall/security settings
- Use public CDN or cloud storage
- Verify DNS resolution

---

#### 3a. Expired or Forbidden URL (400)

**Request:**
```bash
curl -X POST "https://fantastic-endurance-production.up.railway.app/tasks/caption" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://example.com/video.mp4?Expires=1234567890&Signature=abc123",
    "model_size": "small"
  }'
```

**Response:**
```json
{
  "detail": "Unable to access video URL: Access denied (403 Forbidden). The URL may have expired or requires authentication. Please ensure the URL is publicly accessible and not expired."
}
```

**Common Causes:**
- **Signed URLs with expiration**: Many cloud storage services (AWS S3, Alibaba OSS, Google Cloud Storage) generate signed URLs with time-limited access
- **Expired credentials**: URL signatures that have passed their expiration time
- **IP restrictions**: URLs that only work from specific IP addresses
- **Authentication required**: URLs that require login or API keys

**Solution:**
- ✅ Generate a fresh signed URL with longer expiration
- ✅ Use permanent public URLs if available
- ✅ Ensure URL is accessible from any IP address
- ✅ Test URL in browser or curl before submitting
- ✅ For signed URLs, ensure expiration is at least 30 minutes in the future
- ✅ Consider uploading to a public CDN instead

**Example of Good vs Bad URLs:**

```bash
# ❌ BAD: Signed URL with expiration (will fail if expired)
https://storage.example.com/video.mp4?Expires=1759965331&Signature=xyz

# ✅ GOOD: Public URL without expiration
https://cdn.example.com/public/video.mp4

# ✅ GOOD: Signed URL with long expiration (30+ minutes)
https://storage.example.com/video.mp4?Expires=9999999999&Signature=xyz
```

**Note:** The API handles URLs with query parameters correctly (e.g., `?Expires=...&Signature=...`). The URL parsing automatically extracts clean filenames without these parameters.

---

#### 4. Task Not Found (404)

**Request:**
```bash
curl "https://fantastic-endurance-production.up.railway.app/tasks/00000000-0000-0000-0000-000000000000"
```

**Response:**
```json
{
  "detail": "Task not found"
}
```

**Solution:**
- Verify task_id is correct (check for typos)
- Task may have expired (>2 hours old)
- Ensure task was submitted successfully
- Check task submission response

---

#### 5. Video Not Found (404)

**Request:**
```bash
curl "https://fantastic-endurance-production.up.railway.app/video/nonexistent-video.mp4"
```

**Response:**
```json
{
  "detail": "Video not found"
}
```

**Solution:**
- Verify task status is "success" before downloading
- Check filename matches pattern exactly
- Video may have expired (>2 hours)
- Ensure video processing completed

---

#### 6. Scene/Voiceover Count Mismatch (400)

**Request:**
```bash
curl -X POST "https://fantastic-endurance-production.up.railway.app/tasks/merge" \
  -H "Content-Type: application/json" \
  -d '{
    "scene_clip_urls": ["https://example.com/scene1.mp4"],
    "voiceover_urls": [
      "https://example.com/voice1.mp3",
      "https://example.com/voice2.mp3"
    ]
  }'
```

**Response:**
```json
{
  "detail": "Number of scene clips must match number of voiceovers"
}
```

**Solution:**
- Ensure arrays have equal length
- Provide exactly one voiceover per scene
- Check for missing or extra URLs

---

#### 7. Invalid Dimensions (400)

**Request:**
```bash
curl -X POST "https://fantastic-endurance-production.up.railway.app/tasks/merge" \
  -H "Content-Type: application/json" \
  -d '{
    "scene_clip_urls": ["https://example.com/scene1.mp4"],
    "voiceover_urls": ["https://example.com/voice1.mp3"],
    "width": 400,
    "height": 300
  }'
```

**Response:**
```json
{
  "detail": "width must be between 480 and 3840"
}
```

**Solution:**
- Use valid dimension range: 480-3840
- Common presets: 1080×1920 (portrait), 1920×1080 (landscape)
- Ensure both width and height are within range

---

#### 8. Task Failed During Processing

**Status Check Response:**
```json
{
  "task_id": "f7e6d5c4-3b2a-1c0d-9e8f-7a6b5c4d3e2f",
  "status": "failed",
  "video_url": null,
  "error": "FFmpeg processing failed: Invalid video codec - codec not supported",
  "created_at": "2025-10-07T19:00:00.000Z",
  "updated_at": "2025-10-07T19:02:15.000Z",
  "completed_at": "2025-10-07T19:02:15.000Z"
}
```

**Common Failure Reasons:**
- Invalid video format or corrupted file
- Unsupported codec (use H.264)
- Insufficient disk space on server
- Video URL became unreachable during processing
- Out of memory (large Whisper models)
- Invalid audio format

**Solution:**
- Verify video plays correctly locally
- Re-encode to H.264/AAC (MP4)
- Try smaller Whisper model
- Check video file integrity
- Resubmit task after fixing issues

---

### Retry Strategy

**Recommended Retry Logic:**

```python
import time
import requests

def submit_with_retry(url, data, max_retries=3):
    """Submit task with exponential backoff retry"""
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Don't retry client errors (4xx)
            if 400 <= e.response.status_code < 500:
                raise
            # Retry server errors (5xx)
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                print(f"Retry {attempt + 1}/{max_retries} after {wait_time}s")
                time.sleep(wait_time)
            else:
                raise
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Timeout. Retry {attempt + 1}/{max_retries} after {wait_time}s")
                time.sleep(wait_time)
            else:
                raise
```

**Retry Guidelines:**
- ✅ Retry on 5xx errors (server issues)
- ✅ Retry on network timeouts
- ✅ Retry on connection errors
- ❌ Do NOT retry on 4xx errors (client issues)
- ✅ Use exponential backoff (2s, 4s, 8s)
- ✅ Maximum 3 retry attempts
- ✅ Tasks are idempotent (safe to retry)

---

## Code Examples

### Complete Workflow Examples

#### Example 1: Simple Caption Task (cURL + jq)

```bash
#!/bin/bash

BASE_URL="https://fantastic-endurance-production.up.railway.app"

# Submit task
echo "Submitting caption task..."
RESPONSE=$(curl -s -X POST "$BASE_URL/tasks/caption" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://assets.json2video.com/clients/ie2ZO4Au3E/renders/2025-10-06-04355.mp4",
    "model_size": "small"
  }')

TASK_ID=$(echo $RESPONSE | jq -r '.task_id')
echo "Task ID: $TASK_ID"
echo "Status: queued"
echo ""

# Poll for completion
echo "Polling for completion..."
while true; do
  STATUS_RESPONSE=$(curl -s "$BASE_URL/tasks/$TASK_ID")
  STATUS=$(echo $STATUS_RESPONSE | jq -r '.status')

  echo "[$(date +%H:%M:%S)] Status: $STATUS"

  if [ "$STATUS" = "success" ]; then
    VIDEO_URL=$(echo $STATUS_RESPONSE | jq -r '.video_url')
    echo ""
    echo "✓ Video processing complete!"
    echo "Video URL: $VIDEO_URL"
    echo ""

    # Download video
    echo "Downloading video..."
    curl "$VIDEO_URL" -o captioned_output.mp4 --progress-bar
    echo ""
    echo "✓ Downloaded to: captioned_output.mp4"
    break
  elif [ "$STATUS" = "failed" ]; then
    ERROR=$(echo $STATUS_RESPONSE | jq -r '.error')
    echo ""
    echo "✗ Task failed: $ERROR"
    break
  fi

  sleep 5
done
```

**Expected Output:**
```
Submitting caption task...
Task ID: a7f2e8c9-3b1d-4a6e-9c7f-8d2e5b4a1c3d
Status: queued

Polling for completion...
[15:30:00] Status: queued
[15:30:05] Status: running
[15:30:10] Status: running
[15:30:15] Status: running
...
[15:33:45] Status: success

✓ Video processing complete!
Video URL: https://fantastic-endurance-production.up.railway.app/video/a7f2e8c9-3b1d-4a6e-9c7f-8d2e5b4a1c3d_captioned.mp4

Downloading video...
######################################################################## 100.0%

✓ Downloaded to: captioned_output.mp4
```

---

#### Example 2: Python Complete Workflow

```python
import requests
import time
from typing import Optional

BASE_URL = "https://fantastic-endurance-production.up.railway.app"

class VideoProcessingClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()

    def submit_caption_task(self, video_url: str, model_size: str = "small") -> dict:
        """Submit a caption task"""
        print(f"📤 Submitting caption task...")
        print(f"   Video: {video_url}")
        print(f"   Model: {model_size}")

        response = self.session.post(
            f"{self.base_url}/tasks/caption",
            json={
                "video_url": video_url,
                "model_size": model_size
            },
            timeout=30
        )
        response.raise_for_status()
        result = response.json()

        print(f"✓ Task submitted: {result['task_id']}")
        print()
        return result

    def submit_merge_task(
        self,
        scene_clip_urls: list[str],
        voiceover_urls: list[str],
        width: int = 1080,
        height: int = 1920,
        video_volume: float = 0.2,
        voiceover_volume: float = 2.0
    ) -> dict:
        """Submit a merge task"""
        print(f"📤 Submitting merge task...")
        print(f"   Scenes: {len(scene_clip_urls)}")
        print(f"   Dimensions: {width}×{height}")

        response = self.session.post(
            f"{self.base_url}/tasks/merge",
            json={
                "scene_clip_urls": scene_clip_urls,
                "voiceover_urls": voiceover_urls,
                "width": width,
                "height": height,
                "video_volume": video_volume,
                "voiceover_volume": voiceover_volume
            },
            timeout=30
        )
        response.raise_for_status()
        result = response.json()

        print(f"✓ Task submitted: {result['task_id']}")
        print()
        return result

    def submit_background_music_task(
        self,
        video_url: str,
        music_url: str,
        music_volume: float = 0.3,
        video_volume: float = 1.0
    ) -> dict:
        """Submit a background music task"""
        print(f"📤 Submitting background music task...")

        response = self.session.post(
            f"{self.base_url}/tasks/background-music",
            json={
                "video_url": video_url,
                "music_url": music_url,
                "music_volume": music_volume,
                "video_volume": video_volume
            },
            timeout=30
        )
        response.raise_for_status()
        result = response.json()

        print(f"✓ Task submitted: {result['task_id']}")
        print()
        return result

    def get_task_status(self, task_id: str) -> dict:
        """Get task status"""
        response = self.session.get(
            f"{self.base_url}/tasks/{task_id}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    def wait_for_completion(
        self,
        task_id: str,
        poll_interval: int = 5,
        timeout: int = 600
    ) -> Optional[str]:
        """
        Poll task until completion
        Returns video_url on success, raises Exception on failure
        """
        print(f"⏳ Waiting for task to complete...")
        print(f"   Task ID: {task_id}")
        print(f"   Poll interval: {poll_interval}s")
        print()

        start_time = time.time()

        while True:
            elapsed = int(time.time() - start_time)

            if elapsed > timeout:
                raise TimeoutError(
                    f"Task {task_id} exceeded timeout of {timeout}s"
                )

            status_data = self.get_task_status(task_id)
            status = status_data["status"]

            print(f"[{elapsed:>3}s] Status: {status}")

            if status == "success":
                video_url = status_data["video_url"]
                print()
                print(f"✓ Processing complete!")
                print(f"   Duration: {elapsed}s")
                print(f"   Video URL: {video_url}")
                print()
                return video_url
            elif status == "failed":
                error = status_data.get("error", "Unknown error")
                print()
                print(f"✗ Task failed: {error}")
                raise Exception(f"Task failed: {error}")

            time.sleep(poll_interval)

    def download_video(self, video_url: str, output_path: str) -> None:
        """Download processed video"""
        print(f"⬇️  Downloading video...")
        print(f"   Output: {output_path}")

        response = self.session.get(video_url, stream=True, timeout=60)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\r   Progress: {percent:.1f}%", end="", flush=True)

        print()
        print(f"✓ Downloaded: {output_path} ({downloaded / 1024 / 1024:.2f} MB)")
        print()

    def process_video(
        self,
        video_url: str,
        output_path: str,
        model_size: str = "small"
    ) -> str:
        """Complete workflow: submit, wait, download"""
        # Submit task
        task = self.submit_caption_task(video_url, model_size)
        task_id = task["task_id"]

        # Wait for completion
        video_url = self.wait_for_completion(task_id)

        # Download
        self.download_video(video_url, output_path)

        return video_url


# Usage examples
if __name__ == "__main__":
    client = VideoProcessingClient()

    # Example 1: Caption task
    print("=" * 60)
    print("EXAMPLE 1: Caption Task")
    print("=" * 60)
    print()

    try:
        video_url = client.process_video(
            video_url="https://assets.json2video.com/clients/ie2ZO4Au3E/renders/2025-10-06-04355.mp4",
            output_path="captioned_output.mp4",
            model_size="small"
        )
        print(f"🎉 Success! Video URL: {video_url}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print()
    print("=" * 60)
    print("EXAMPLE 2: Merge Task")
    print("=" * 60)
    print()

    # Example 2: Merge task
    try:
        task = client.submit_merge_task(
            scene_clip_urls=[
                "https://dashscope-result-sh.oss-cn-shanghai.aliyuncs.com/1d/ec/20251006/621d405c/d4ca0899-3ae0-4e39-a1ad-72c566cb523e.mp4",
                "https://dashscope-result-sh.oss-cn-shanghai.aliyuncs.com/1d/95/20251006/bd55ff35/f8136329-edf4-42ef-b2f9-41e6c150bc89.mp4"
            ],
            voiceover_urls=[
                "https://v3.fal.media/files/koala/R9xah-zpIWdujeJVfI_Lh_output.mp3",
                "https://v3.fal.media/files/rabbit/0UNjgXiomqsqpRwtebRTj_output.mp3"
            ]
        )

        video_url = client.wait_for_completion(task["task_id"])
        client.download_video(video_url, "merged_output.mp4")
        print(f"🎉 Success! Video URL: {video_url}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print()
    print("=" * 60)
    print("EXAMPLE 3: Background Music Task")
    print("=" * 60)
    print()

    # Example 3: Background music
    try:
        task = client.submit_background_music_task(
            video_url="https://assets.json2video.com/clients/ie2ZO4Au3E/renders/2025-10-06-26438.mp4",
            music_url="https://v3.fal.media/files/zebra/m8xVxf5xojnXa8SB5oUnd_normalized_audio.wav",
            music_volume=0.3
        )

        video_url = client.wait_for_completion(task["task_id"])
        client.download_video(video_url, "with_music_output.mp4")
        print(f"🎉 Success! Video URL: {video_url}")
    except Exception as e:
        print(f"❌ Error: {e}")
```

**Expected Output:**
```
============================================================
EXAMPLE 1: Caption Task
============================================================

📤 Submitting caption task...
   Video: https://assets.json2video.com/clients/ie2ZO4Au3E/renders/2025-10-06-04355.mp4
   Model: small
✓ Task submitted: a7f2e8c9-3b1d-4a6e-9c7f-8d2e5b4a1c3d

⏳ Waiting for task to complete...
   Task ID: a7f2e8c9-3b1d-4a6e-9c7f-8d2e5b4a1c3d
   Poll interval: 5s

[  0s] Status: queued
[  5s] Status: queued
[ 10s] Status: running
[ 15s] Status: running
[ 20s] Status: running
...
[185s] Status: success

✓ Processing complete!
   Duration: 185s
   Video URL: https://fantastic-endurance-production.up.railway.app/video/a7f2e8c9-3b1d-4a6e-9c7f-8d2e5b4a1c3d_captioned.mp4

⬇️  Downloading video...
   Output: captioned_output.mp4
   Progress: 100.0%
✓ Downloaded: captioned_output.mp4 (15.23 MB)

🎉 Success! Video URL: https://fantastic-endurance-production.up.railway.app/video/a7f2e8c9-3b1d-4a6e-9c7f-8d2e5b4a1c3d_captioned.mp4
```

---

#### Example 3: JavaScript/Node.js Complete Workflow

```javascript
const axios = require('axios');
const fs = require('fs');

const BASE_URL = 'https://fantastic-endurance-production.up.railway.app';

class VideoProcessingClient {
  constructor(baseUrl = BASE_URL) {
    this.baseUrl = baseUrl;
    this.client = axios.create({
      baseURL: baseUrl,
      timeout: 30000
    });
  }

  async submitCaptionTask(videoUrl, modelSize = 'small') {
    console.log('📤 Submitting caption task...');
    console.log(`   Video: ${videoUrl}`);
    console.log(`   Model: ${modelSize}`);

    const response = await this.client.post('/tasks/caption', {
      video_url: videoUrl,
      model_size: modelSize
    });

    console.log(`✓ Task submitted: ${response.data.task_id}`);
    console.log();
    return response.data;
  }

  async submitMergeTask(sceneClipUrls, voiceoverUrls, options = {}) {
    console.log('📤 Submitting merge task...');
    console.log(`   Scenes: ${sceneClipUrls.length}`);

    const response = await this.client.post('/tasks/merge', {
      scene_clip_urls: sceneClipUrls,
      voiceover_urls: voiceoverUrls,
      width: options.width || 1080,
      height: options.height || 1920,
      video_volume: options.videoVolume || 0.2,
      voiceover_volume: options.voiceoverVolume || 2.0
    });

    console.log(`✓ Task submitted: ${response.data.task_id}`);
    console.log();
    return response.data;
  }

  async submitBackgroundMusicTask(videoUrl, musicUrl, options = {}) {
    console.log('📤 Submitting background music task...');

    const response = await this.client.post('/tasks/background-music', {
      video_url: videoUrl,
      music_url: musicUrl,
      music_volume: options.musicVolume || 0.3,
      video_volume: options.videoVolume || 1.0
    });

    console.log(`✓ Task submitted: ${response.data.task_id}`);
    console.log();
    return response.data;
  }

  async getTaskStatus(taskId) {
    const response = await this.client.get(`/tasks/${taskId}`);
    return response.data;
  }

  async waitForCompletion(taskId, pollInterval = 5000, timeout = 600000) {
    console.log('⏳ Waiting for task to complete...');
    console.log(`   Task ID: ${taskId}`);
    console.log(`   Poll interval: ${pollInterval / 1000}s`);
    console.log();

    const startTime = Date.now();

    while (true) {
      const elapsed = Math.floor((Date.now() - startTime) / 1000);

      if (Date.now() - startTime > timeout) {
        throw new Error(`Task ${taskId} exceeded timeout of ${timeout}ms`);
      }

      const statusData = await this.getTaskStatus(taskId);
      const status = statusData.status;

      console.log(`[${elapsed.toString().padStart(3)}s] Status: ${status}`);

      if (status === 'success') {
        console.log();
        console.log('✓ Processing complete!');
        console.log(`   Duration: ${elapsed}s`);
        console.log(`   Video URL: ${statusData.video_url}`);
        console.log();
        return statusData.video_url;
      } else if (status === 'failed') {
        console.log();
        console.log(`✗ Task failed: ${statusData.error}`);
        throw new Error(`Task failed: ${statusData.error}`);
      }

      await new Promise(resolve => setTimeout(resolve, pollInterval));
    }
  }

  async downloadVideo(videoUrl, outputPath) {
    console.log('⬇️  Downloading video...');
    console.log(`   Output: ${outputPath}`);

    const response = await axios.get(videoUrl, {
      responseType: 'stream'
    });

    const writer = fs.createWriteStream(outputPath);
    response.data.pipe(writer);

    return new Promise((resolve, reject) => {
      writer.on('finish', () => {
        console.log(`✓ Downloaded: ${outputPath}`);
        console.log();
        resolve();
      });
      writer.on('error', reject);
    });
  }

  async processVideo(videoUrl, outputPath, modelSize = 'small') {
    // Submit task
    const task = await this.submitCaptionTask(videoUrl, modelSize);
    const taskId = task.task_id;

    // Wait for completion
    const resultVideoUrl = await this.waitForCompletion(taskId);

    // Download
    await this.downloadVideo(resultVideoUrl, outputPath);

    return resultVideoUrl;
  }
}

// Usage examples
(async () => {
  const client = new VideoProcessingClient();

  // Example 1: Caption task
  console.log('='.repeat(60));
  console.log('EXAMPLE 1: Caption Task');
  console.log('='.repeat(60));
  console.log();

  try {
    const videoUrl = await client.processVideo(
      'https://assets.json2video.com/clients/ie2ZO4Au3E/renders/2025-10-06-04355.mp4',
      'captioned_output.mp4',
      'small'
    );
    console.log(`🎉 Success! Video URL: ${videoUrl}`);
  } catch (error) {
    console.error(`❌ Error: ${error.message}`);
  }

  console.log();
  console.log('='.repeat(60));
  console.log('EXAMPLE 2: Merge Task');
  console.log('='.repeat(60));
  console.log();

  // Example 2: Merge task
  try {
    const task = await client.submitMergeTask(
      [
        'https://dashscope-result-sh.oss-cn-shanghai.aliyuncs.com/1d/ec/20251006/621d405c/d4ca0899-3ae0-4e39-a1ad-72c566cb523e.mp4',
        'https://dashscope-result-sh.oss-cn-shanghai.aliyuncs.com/1d/95/20251006/bd55ff35/f8136329-edf4-42ef-b2f9-41e6c150bc89.mp4'
      ],
      [
        'https://v3.fal.media/files/koala/R9xah-zpIWdujeJVfI_Lh_output.mp3',
        'https://v3.fal.media/files/rabbit/0UNjgXiomqsqpRwtebRTj_output.mp3'
      ]
    );

    const videoUrl = await client.waitForCompletion(task.task_id);
    await client.downloadVideo(videoUrl, 'merged_output.mp4');
    console.log(`🎉 Success! Video URL: ${videoUrl}`);
  } catch (error) {
    console.error(`❌ Error: ${error.message}`);
  }

  console.log();
  console.log('='.repeat(60));
  console.log('EXAMPLE 3: Background Music Task');
  console.log('='.repeat(60));
  console.log();

  // Example 3: Background music
  try {
    const task = await client.submitBackgroundMusicTask(
      'https://assets.json2video.com/clients/ie2ZO4Au3E/renders/2025-10-06-26438.mp4',
      'https://v3.fal.media/files/zebra/m8xVxf5xojnXa8SB5oUnd_normalized_audio.wav',
      { musicVolume: 0.3 }
    );

    const videoUrl = await client.waitForCompletion(task.task_id);
    await client.downloadVideo(videoUrl, 'with_music_output.mp4');
    console.log(`🎉 Success! Video URL: ${videoUrl}`);
  } catch (error) {
    console.error(`❌ Error: ${error.message}`);
  }
})();
```

---

### Browser Integration Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Video Processing API Demo</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 800px;
      margin: 50px auto;
      padding: 20px;
    }
    .section {
      background: #f5f5f5;
      padding: 20px;
      margin: 20px 0;
      border-radius: 8px;
    }
    input, select, button {
      padding: 10px;
      margin: 5px 0;
      width: 100%;
      box-sizing: border-box;
    }
    button {
      background: #007bff;
      color: white;
      border: none;
      cursor: pointer;
      border-radius: 5px;
    }
    button:hover {
      background: #0056b3;
    }
    button:disabled {
      background: #ccc;
      cursor: not-allowed;
    }
    #status {
      padding: 15px;
      margin: 20px 0;
      border-radius: 5px;
      font-weight: bold;
    }
    .success { background: #d4edda; color: #155724; }
    .error { background: #f8d7da; color: #721c24; }
    .info { background: #d1ecf1; color: #0c5460; }
    video {
      width: 100%;
      max-width: 640px;
      border-radius: 8px;
      margin: 20px 0;
    }
  </style>
</head>
<body>
  <h1>🎬 Video Processing API Demo</h1>

  <div class="section">
    <h2>Submit Caption Task</h2>
    <input type="text" id="videoUrl" placeholder="Enter video URL"
           value="https://assets.json2video.com/clients/ie2ZO4Au3E/renders/2025-10-06-04355.mp4">
    <select id="modelSize">
      <option value="tiny">Tiny (Fastest)</option>
      <option value="base">Base</option>
      <option value="small" selected>Small (Recommended)</option>
      <option value="medium">Medium</option>
      <option value="large">Large (Best Quality)</option>
    </select>
    <button onclick="submitCaptionTask()" id="submitBtn">Submit Task</button>
  </div>

  <div id="status"></div>

  <div id="resultSection" style="display: none;">
    <h2>✓ Processing Complete!</h2>
    <video id="resultVideo" controls></video>
    <br>
    <a id="downloadLink" download="captioned_video.mp4">
      <button>Download Video</button>
    </a>
  </div>

  <script>
    const BASE_URL = 'https://fantastic-endurance-production.up.railway.app';
    let pollInterval;

    function showStatus(message, type = 'info') {
      const statusDiv = document.getElementById('status');
      statusDiv.textContent = message;
      statusDiv.className = type;
      statusDiv.style.display = 'block';
    }

    async function submitCaptionTask() {
      const videoUrl = document.getElementById('videoUrl').value;
      const modelSize = document.getElementById('modelSize').value;
      const submitBtn = document.getElementById('submitBtn');

      if (!videoUrl) {
        showStatus('Please enter a video URL', 'error');
        return;
      }

      submitBtn.disabled = true;
      document.getElementById('resultSection').style.display = 'none';

      try {
        showStatus('Submitting task...', 'info');

        const response = await fetch(`${BASE_URL}/tasks/caption`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            video_url: videoUrl,
            model_size: modelSize
          })
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || 'Request failed');
        }

        const data = await response.json();
        showStatus(`Task submitted! ID: ${data.task_id}`, 'success');

        // Start polling
        pollTaskStatus(data.task_id);

      } catch (error) {
        showStatus(`Error: ${error.message}`, 'error');
        submitBtn.disabled = false;
      }
    }

    async function pollTaskStatus(taskId) {
      const submitBtn = document.getElementById('submitBtn');
      let pollCount = 0;

      pollInterval = setInterval(async () => {
        try {
          const response = await fetch(`${BASE_URL}/tasks/${taskId}`);
          const data = await response.json();

          pollCount++;
          const elapsed = pollCount * 5;

          if (data.status === 'success') {
            clearInterval(pollInterval);
            showStatus(`Processing complete! (${elapsed}s)`, 'success');
            showResult(data.video_url);
            submitBtn.disabled = false;
          } else if (data.status === 'failed') {
            clearInterval(pollInterval);
            showStatus(`Task failed: ${data.error}`, 'error');
            submitBtn.disabled = false;
          } else {
            showStatus(`Processing... Status: ${data.status} (${elapsed}s)`, 'info');
          }

        } catch (error) {
          clearInterval(pollInterval);
          showStatus(`Error checking status: ${error.message}`, 'error');
          submitBtn.disabled = false;
        }
      }, 5000);
    }

    function showResult(videoUrl) {
      const resultSection = document.getElementById('resultSection');
      const resultVideo = document.getElementById('resultVideo');
      const downloadLink = document.getElementById('downloadLink');

      resultVideo.src = videoUrl;
      downloadLink.href = videoUrl;
      resultSection.style.display = 'block';

      // Scroll to result
      resultSection.scrollIntoView({ behavior: 'smooth' });
    }
  </script>
</body>
</html>
```

---

## Rate Limits and Constraints

### File Size Limits

| Operation | Per-File Limit | Total Limit | Configurable |
|-----------|----------------|-------------|--------------|
| Caption | 100MB | 100MB | Yes (MAX_FILE_SIZE_MB) |
| Background Music | 100MB per file | 200MB combined | Yes (2× MAX_FILE_SIZE_MB) |
| Merge | 100MB per file | 500MB combined | Yes (5× MAX_FILE_SIZE_MB) |

**Example File Size Checks:**

```bash
# Check file size before submission
curl -I "https://example.com/video.mp4" | grep -i content-length

# Expected output
Content-Length: 52428800  # 50MB (within limit)
```

### Processing Limits

| Limit Type | Default Value | Configurable | Environment Variable |
|------------|---------------|--------------|---------------------|
| Concurrent workers per instance | 3 | Yes | MAX_CONCURRENT_WORKERS |
| Queue size | Unlimited | No | N/A |
| Task timeout | None (runs to completion) | No | N/A |
| Video expiration | 2 hours | Yes | TASK_TTL_HOURS |
| Whisper model cache | Persists across tasks | No | WHISPER_MODEL_CACHE_DIR |

### Format Support

**Video Formats:**
- ✅ MP4 (H.264, H.265/HEVC)
- ✅ MOV (QuickTime)
- ✅ AVI
- ✅ MKV (Matroska)
- ✅ WebM
- ✅ FLV
- ❌ Proprietary formats (WMV, AVCHD)

**Audio Formats:**
- ✅ MP3
- ✅ WAV
- ✅ AAC
- ✅ M4A
- ✅ FLAC
- ✅ OGG
- ❌ Proprietary formats (WMA)

**Recommended Formats:**
- Video: MP4 with H.264 video codec and AAC audio codec
- Audio: MP3 or AAC

### Dimension Constraints

**Merge Task Dimensions:**
- **Minimum**: 480×480 pixels
- **Maximum**: 3840×3840 pixels (4K)
- **Common Presets**:
  - Portrait (Social Media): 1080×1920
  - Landscape (YouTube): 1920×1080
  - Square (Instagram): 1080×1080
  - 4K Landscape: 3840×2160

**Example Valid Dimensions:**
```json
{"width": 1080, "height": 1920}  // ✅ Portrait
{"width": 1920, "height": 1080}  // ✅ Landscape
{"width": 1080, "height": 1080}  // ✅ Square
{"width": 1280, "height": 720}   // ✅ HD
{"width": 3840, "height": 2160}  // ✅ 4K
{"width": 400, "height": 300}    // ❌ Too small
{"width": 5000, "height": 3000}  // ❌ Too large
```

### Whisper Model Sizes and Performance

| Model | Size | RAM Usage | Speed | Accuracy | Best For |
|-------|------|-----------|-------|----------|----------|
| tiny | 75MB | ~1GB | 32x | ⭐⭐ | Testing, simple speech |
| base | 140MB | ~1GB | 16x | ⭐⭐⭐ | Clear audio, short clips |
| small | 465MB | ~2GB | 6x | ⭐⭐⭐⭐ | General use (default) |
| medium | 1.5GB | ~5GB | 2x | ⭐⭐⭐⭐⭐ | Noisy audio, accents |
| large | 2.9GB | ~10GB | 1x | ⭐⭐⭐⭐⭐ | Professional transcription |

**Processing Time Estimates:**

```
Video Duration: 5 minutes (300 seconds)

tiny:   150 seconds (2.5 minutes)
base:   225 seconds (3.75 minutes)
small:  300 seconds (5 minutes)
medium: 600 seconds (10 minutes)
large:  900 seconds (15 minutes)
```

### Scaling Considerations

**Horizontal Scaling:**
- **Web servers**: Stateless, scale infinitely behind load balancer
- **Workers**: Each processes 3 concurrent tasks (configurable)
- **Redis**: Single shared queue across all workers
- **Supabase**: Managed service, auto-scales

**Capacity Planning Example:**

```
Target: Process 50 concurrent tasks

Web Servers:
- 3 instances behind load balancer
- Each handles ~100 req/s

Workers:
- 17 instances (50 tasks ÷ 3 tasks/instance)
- Each instance: 2 CPU cores, 4GB RAM

Redis:
- 1 instance (single queue)
- 1GB RAM sufficient

Supabase:
- Auto-scales based on load
- No manual configuration needed
```

**Worker Scaling Formula:**
```
Required Workers = Ceiling(Concurrent Tasks ÷ MAX_CONCURRENT_WORKERS)

Examples:
- 10 tasks, 3 workers/instance = 4 instances
- 30 tasks, 3 workers/instance = 10 instances
- 100 tasks, 5 workers/instance = 20 instances
```

---

## Configuration

### Environment Variables

#### Required Variables

```bash
# Supabase Database
Database_URL=https://your-project.supabase.co
Database_ANON_KEY=your-anon-key-here

# Redis Queue
REDIS_URL=redis://red-xyz123.railway.app:6379
```

#### Optional Variables

```bash
# Server Configuration
PORT=8000
RAILWAY_PUBLIC_URL=https://fantastic-endurance-production.up.railway.app

# File Size and Processing
MAX_FILE_SIZE_MB=100
MAX_CONCURRENT_WORKERS=3
TASK_TTL_HOURS=2

# Storage Directories
VIDEO_OUTPUT_DIR=/tmp/videos
WHISPER_MODEL_CACHE_DIR=/tmp/whisper_cache
```

### Configuration Reference

| Variable | Type | Default | Description | Example |
|----------|------|---------|-------------|---------|
| Database_URL | string | None | Supabase project URL | https://abc123.supabase.co |
| Database_ANON_KEY | string | None | Supabase anonymous key | eyJhbGciOiJIUz... |
| REDIS_URL | string | redis://localhost:6379 | Redis connection string | redis://red-xyz.railway.app:6379 |
| PORT | integer | 8000 | Web server port | 8000 |
| RAILWAY_PUBLIC_URL | string | http://localhost:8000 | Public URL for video links | https://fantastic-endurance-production.up.railway.app |
| MAX_FILE_SIZE_MB | integer | 100 | Maximum file size per file | 150 |
| MAX_CONCURRENT_WORKERS | integer | 3 | Concurrent tasks per worker | 5 |
| TASK_TTL_HOURS | integer | 2 | Hours before video cleanup | 3 |
| VIDEO_OUTPUT_DIR | string | ./videos | Directory for processed videos | /tmp/videos |
| WHISPER_MODEL_CACHE_DIR | string | ./whisper_cache | Directory for Whisper models | /tmp/whisper_cache |

### Railway Deployment

**Automatic Configuration:**

Railway automatically provides:
- `REDIS_URL`: Set to Railway Redis instance
- `PORT`: Assigned dynamically
- `RAILWAY_PUBLIC_DOMAIN`: Your app's public URL

**Set These Manually:**
1. Go to Railway Dashboard
2. Select your service
3. Click "Variables" tab
4. Add:
   - `Database_URL`
   - `Database_ANON_KEY`
   - `MAX_FILE_SIZE_MB` (optional)
   - `MAX_CONCURRENT_WORKERS` (optional)

---

## Security

### Current Security Model

⚠️ **Important**: The API currently has **no authentication** and is **publicly accessible**.

**Suitable For:**
- Development and testing
- Internal networks
- Trusted environments
- MVP/proof-of-concept

**Not Suitable For:**
- Public production deployment
- Handling sensitive videos
- Multi-tenant applications
- Commercial use without modifications

### Production Security Recommendations

#### 1. Add API Key Authentication

Protect endpoints with API key:

```python
from fastapi import Security, HTTPException, Depends
from fastapi.security import APIKeyHeader
import os

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    correct_api_key = os.getenv("API_SECRET_KEY")
    if not api_key or api_key != correct_api_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing API key"
        )
    return api_key

# Apply to endpoints
@router.post("/tasks/caption", dependencies=[Depends(verify_api_key)])
async def create_caption_task(...):
    ...
```

**Client Usage:**
```bash
curl -X POST "https://fantastic-endurance-production.up.railway.app/tasks/caption" \
  -H "X-API-Key: your-secret-key-here" \
  -H "Content-Type: application/json" \
  -d '{"video_url": "...", "model_size": "small"}'
```

#### 2. Rate Limiting

Prevent abuse with rate limits:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/tasks/caption")
@limiter.limit("10/minute")  # 10 requests per minute
async def create_caption_task(request: Request, ...):
    ...
```

#### 3. CORS Configuration

Restrict allowed origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://app.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)
```

### Best Practices

**For API Operators:**
- ✅ Enable authentication in production
- ✅ Use HTTPS with valid SSL certificates
- ✅ Implement rate limiting per IP/user
- ✅ Monitor for abuse and unusual patterns
- ✅ Rotate API keys regularly
- ✅ Use environment variables for secrets
- ✅ Enable audit logging
- ✅ Restrict CORS origins
- ✅ Set up monitoring and alerts
- ✅ Implement request validation

**For API Consumers:**
- ✅ Never commit API keys to repositories
- ✅ Use HTTPS for all requests
- ✅ Validate video URLs before submission
- ✅ Implement timeout handling
- ✅ Use secure video URL storage
- ✅ Download videos before expiration
- ✅ Handle errors gracefully
- ✅ Implement retry logic
- ✅ Monitor API usage and costs

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Worker Not Processing Tasks

**Symptoms:**
- Tasks stuck in "queued" status indefinitely
- Queue length increasing continuously
- No status updates after submission

**Diagnosis:**
```bash
# Check queue status
curl "https://fantastic-endurance-production.up.railway.app/debug/queue"

# Check health
curl "https://fantastic-endurance-production.up.railway.app/health"

# Expected healthy response:
# {"status": "healthy", "redis": "connected", "supabase": "connected", "queue_length": 5}
```

**Solutions:**
- ✅ Verify worker process is running (check Railway dashboard)
- ✅ Check worker logs for errors
- ✅ Verify REDIS_URL environment variable
- ✅ Restart worker service
- ✅ Check Redis connection limits
- ✅ Verify sufficient worker resources (CPU/RAM)

---

#### 2. Videos Not Found After Completion

**Symptoms:**
- Task status shows "success"
- video_url returns 404 error
- Download links don't work

**Diagnosis:**
```bash
# Check task status
curl "https://fantastic-endurance-production.up.railway.app/tasks/{task_id}"

# Try downloading directly
curl -I "https://fantastic-endurance-production.up.railway.app/video/{filename}"

# Check video expiration time
# Videos expire 2 hours after completion
```

**Solutions:**
- ✅ Verify RAILWAY_PUBLIC_URL matches deployment URL
- ✅ Check video hasn't expired (>2 hours)
- ✅ Verify VIDEO_OUTPUT_DIR is correctly configured
- ✅ Check worker has write permissions
- ✅ Ensure sufficient disk space
- ✅ Check filename pattern matches exactly

---

#### 3. Slow Processing Times

**Symptoms:**
- Tasks taking much longer than expected
- Queue backlog building up
- Timeouts occurring

**Diagnosis:**
```bash
# Check queue length
curl "https://fantastic-endurance-production.up.railway.app/debug/queue"

# Monitor task progression
watch -n 5 'curl -s "https://fantastic-endurance-production.up.railway.app/tasks/{task_id}" | jq .status'
```

**Solutions:**
- ✅ Use smaller Whisper model (tiny, base, small)
- ✅ Increase MAX_CONCURRENT_WORKERS
- ✅ Deploy additional worker instances
- ✅ Upgrade worker resources (more CPU cores)
- ✅ Optimize video before submission (lower resolution)
- ✅ Process shorter videos in batches

**Processing Time Comparison:**
```
5-minute video with different models:

tiny:   2.5 minutes  (🟢 Fast)
base:   3.75 minutes (🟢 Fast)
small:  5 minutes    (🟡 Medium)
medium: 10 minutes   (🔴 Slow)
large:  15 minutes   (🔴 Very Slow)
```

---

#### 4. Out of Memory Errors

**Symptoms:**
- Worker crashes during processing
- Tasks fail with "Out of memory" error
- Large Whisper models fail consistently

**Diagnosis:**
```bash
# Check task error message
curl "https://fantastic-endurance-production.up.railway.app/tasks/{task_id}"

# Look for errors like:
# "error": "Worker crashed: Out of memory"
```

**Solutions:**
- ✅ Use smaller Whisper model
- ✅ Increase worker memory allocation (Railway: Upgrade plan)
- ✅ Process shorter videos
- ✅ Reduce MAX_CONCURRENT_WORKERS
- ✅ Enable swap if available

**Memory Requirements:**
```
Model Memory Usage:
tiny:   ~1GB RAM
base:   ~1GB RAM
small:  ~2GB RAM
medium: ~5GB RAM
large:  ~10GB RAM

Recommended Worker Memory:
tiny/base:  2GB
small:      4GB
medium:     8GB
large:      16GB
```

---

#### 5. FFmpeg Errors

**Symptoms:**
- Tasks fail with FFmpeg-related errors
- Error messages mention codecs or formats
- Video format not supported

**Common Error Messages:**
```json
{
  "error": "FFmpeg processing failed: Unknown codec"
}
{
  "error": "FFmpeg processing failed: Invalid video format"
}
```

**Solutions:**
- ✅ Use standard formats (H.264 video, AAC audio)
- ✅ Re-encode video to MP4 before submission
- ✅ Verify video file isn't corrupted
- ✅ Check video codec with:

```bash
# Check video codec
ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name \
  -of default=noprint_wrappers=1:nokey=1 \
  video.mp4

# Expected output: h264
```

**Recommended FFmpeg Command for Re-encoding:**
```bash
ffmpeg -i input.mp4 \
  -c:v libx264 -preset medium -crf 23 \
  -c:a aac -b:a 128k \
  -movflags +faststart \
  output.mp4
```

---

#### 6. Task Stuck in "Running" Status

**Symptoms:**
- Status stuck on "running" for extended period
- No completion or failure after expected time
- Worker appears to hang

**Diagnosis:**
```bash
# Poll status multiple times
for i in {1..10}; do
  curl -s "https://fantastic-endurance-production.up.railway.app/tasks/{task_id}" | jq '.status, .updated_at'
  sleep 10
done

# Check if updated_at is changing
```

**Solutions:**
- ✅ Wait longer (large models take time)
- ✅ Check worker logs for progress
- ✅ Verify worker hasn't crashed
- ✅ Check disk space isn't full
- ✅ Restart worker if truly stuck
- ✅ Resubmit task if necessary

---

### Diagnostic Checklist

When troubleshooting, check these in order:

**1. API Health**
```bash
curl "https://fantastic-endurance-production.up.railway.app/health"
```
✅ Status: healthy
✅ Redis: connected
✅ Supabase: connected

**2. Queue Status**
```bash
curl "https://fantastic-endurance-production.up.railway.app/debug/queue"
```
✅ Redis connected
✅ Queue length reasonable (<100)

**3. Task Status**
```bash
curl "https://fantastic-endurance-production.up.railway.app/tasks/{task_id}"
```
✅ Task found
✅ Status progressing (queued → running → success/failed)
✅ updated_at changing

**4. Video Availability**
```bash
curl -I "https://fantastic-endurance-production.up.railway.app/video/{filename}"
```
✅ Status: 200 OK
✅ Content-Type: video/mp4
✅ Content-Length > 0

---

### Getting Help

**Resources:**
- 📚 This documentation (API_DOCS.md)
- 🏗️ Architecture guide (ARCHITECTURE.md)
- 🚀 Deployment guide (DEPLOYMENT.md)
- 💡 Usage examples (EXAMPLES.md)
- 🔍 Interactive API docs: https://fantastic-endurance-production.up.railway.app/docs

**Health Check:**
```bash
curl "https://fantastic-endurance-production.up.railway.app/health"
```

**Debug Info:**
```bash
curl "https://fantastic-endurance-production.up.railway.app/debug/queue"
```

---

## Interactive Documentation

The API includes built-in interactive documentation powered by FastAPI.

### Swagger UI (Recommended)

**URL:** `https://fantastic-endurance-production.up.railway.app/docs`

**Features:**
- ✅ Try out all endpoints directly in browser
- ✅ View request/response schemas
- ✅ See example payloads
- ✅ Test authentication
- ✅ Response code documentation
- ✅ Model definitions
- ✅ Download OpenAPI spec

**Usage:**
1. Navigate to /docs
2. Click on an endpoint to expand
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"
6. View response

### ReDoc

**URL:** `https://fantastic-endurance-production.up.railway.app/redoc`

**Features:**
- ✅ Beautiful, readable API documentation
- ✅ Organized by tags and operations
- ✅ Detailed schema documentation
- ✅ Request/response examples
- ✅ Three-column layout
- ✅ Search functionality
- ✅ Downloadable specification

### HTML Interface

**URL:** `https://fantastic-endurance-production.up.railway.app/`

**Features:**
- ✅ Welcome page with API overview
- ✅ Quick start guide
- ✅ Links to documentation
- ✅ Usage examples
- ✅ Endpoint summaries

### OpenAPI Specification

**URL:** `https://fantastic-endurance-production.up.railway.app/openapi.json`

The API exposes a complete OpenAPI 3.0 specification that can be:
- 📥 Imported into Postman
- 🔧 Used with code generators
- 🌐 Integrated with API gateways
- ✅ Validated with OpenAPI tools
- 📚 Used for documentation generation

**Download Spec:**
```bash
curl "https://fantastic-endurance-production.up.railway.app/openapi.json" \
  -o api-spec.json
```

---

## FAQ

### General Questions

**Q: Is there a rate limit?**
A: No built-in rate limit currently. Implement rate limiting in production using middleware or reverse proxy.

**Q: How long do videos remain available?**
A: Videos expire and are deleted 2 hours after completion. Download them promptly.

**Q: Can I use this API in production?**
A: Yes, but add authentication, rate limiting, and monitoring first.

**Q: What video formats are supported?**
A: MP4, MOV, AVI, MKV, WebM with H.264/H.265 video codecs.

**Q: Is there a file size limit?**
A: Yes, 100MB per file by default. Configurable via MAX_FILE_SIZE_MB.

**Q: Do I need an API key?**
A: No, the API is currently open. Consider adding authentication for production.

### Technical Questions

**Q: How do I know when my video is ready?**
A: Poll GET /tasks/{task_id} every 5 seconds until status is "success".

**Q: Can I process multiple videos simultaneously?**
A: Yes, submit multiple tasks. Each worker processes 3 concurrent tasks.

**Q: What happens if a task fails?**
A: Status becomes "failed" with error message. Resubmit after fixing issues.

**Q: Can I cancel a queued task?**
A: No cancellation endpoint currently. Task will process when worker picks it up.

**Q: Do you support webhooks for completion notifications?**
A: Not currently. You must poll for status updates.

**Q: What's the maximum video length?**
A: Limited only by file size (100MB). Typical max: 10-20 minutes at standard quality.

### Processing Questions

**Q: How accurate are the captions?**
A: Depends on Whisper model size and audio quality. "small" model is good for general use. "large" provides best accuracy.

**Q: Can I customize subtitle styling?**
A: Not currently. Subtitles use white text with black outline, optimized for readability.

**Q: Which Whisper model should I use?**
A:
- **tiny/base**: Testing, simple speech
- **small**: General use (recommended)
- **medium/large**: Noisy audio, accents, professional use

**Q: Can I merge more than 10 scenes?**
A: Yes, but total size must stay under 500MB (5× MAX_FILE_SIZE_MB).

**Q: Why is my caption task slow?**
A: Processing time depends on video length and model size. Use smaller models for faster results.

---

## Changelog

### Version 1.0.0 (October 2025)

**Initial Release:**
- ✅ Video captioning with Whisper (5 model sizes)
- ✅ Video merging with voiceovers (unlimited scenes)
- ✅ Background music addition with volume control
- ✅ Asynchronous task queue (Redis)
- ✅ Health monitoring and diagnostics
- ✅ Automatic cleanup (2-hour TTL)
- ✅ REST API with OpenAPI docs
- ✅ Railway deployment support
- ✅ Comprehensive error handling
- ✅ File size validation
- ✅ Multiple format support

---

## Quick Reference

### Base URL
```
https://fantastic-endurance-production.up.railway.app
```

### Essential Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/tasks/caption` | POST | Submit caption task |
| `/tasks/merge` | POST | Submit merge task |
| `/tasks/background-music` | POST | Submit background music task |
| `/tasks/{task_id}` | GET | Get task status |
| `/video/{filename}` | GET | Download video |
| `/health` | GET | Check API health |
| `/docs` | GET | Interactive documentation |

### Quick Start Command

```bash
# Submit, poll, and download in one script
TASK=$(curl -s -X POST "https://fantastic-endurance-production.up.railway.app/tasks/caption" \
  -H "Content-Type: application/json" \
  -d '{"video_url":"https://example.com/video.mp4","model_size":"small"}' \
  | jq -r '.task_id') && \
while true; do
  STATUS=$(curl -s "https://fantastic-endurance-production.up.railway.app/tasks/$TASK" | jq -r '.status')
  echo "Status: $STATUS"
  if [ "$STATUS" = "success" ]; then
    URL=$(curl -s "https://fantastic-endurance-production.up.railway.app/tasks/$TASK" | jq -r '.video_url')
    curl "$URL" -o output.mp4
    break
  fi
  sleep 5
done
```

---

**End of Documentation**

For more information, visit:
- 🌐 API: https://fantastic-endurance-production.up.railway.app
- 📚 Interactive Docs: https://fantastic-endurance-production.up.railway.app/docs
- 📖 ReDoc: https://fantastic-endurance-production.up.railway.app/redoc
