# Quick Reference Guide

## API Base URL
```
https://fantastic-endurance-production.up.railway.app
```

## Essential Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/tasks/caption` | POST | Add subtitles to video |
| `/tasks/merge` | POST | Merge scenes with voiceovers |
| `/tasks/background-music` | POST | Add background music |
| `/tasks/{task_id}` | GET | Check task status |
| `/video/{filename}` | GET | Download processed video |
| `/health` | GET | Check API health |
| `/docs` | GET | Interactive documentation |

## Common Tasks

### 1. Add Captions to Video

```bash
# Submit task
curl -X POST "https://fantastic-endurance-production.up.railway.app/tasks/caption" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://example.com/video.mp4",
    "model_size": "small"
  }'

# Response: {"task_id": "abc-123", "status": "queued", ...}

# Check status
curl "https://fantastic-endurance-production.up.railway.app/tasks/abc-123"

# Download when complete
curl "https://fantastic-endurance-production.up.railway.app/video/abc-123_captioned.mp4" -o output.mp4
```

### 2. Merge Videos with Voiceovers

```bash
curl -X POST "https://fantastic-endurance-production.up.railway.app/tasks/merge" \
  -H "Content-Type: application/json" \
  -d '{
    "scene_clip_urls": [
      "https://example.com/scene1.mp4",
      "https://example.com/scene2.mp4"
    ],
    "voiceover_urls": [
      "https://example.com/voice1.mp3",
      "https://example.com/voice2.mp3"
    ],
    "width": 1080,
    "height": 1920
  }'
```

### 3. Add Background Music

```bash
curl -X POST "https://fantastic-endurance-production.up.railway.app/tasks/background-music" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://example.com/video.mp4",
    "music_url": "https://example.com/music.mp3",
    "music_volume": 0.3
  }'
```

## Status Values

| Status | Description |
|--------|-------------|
| `queued` | Task waiting in queue |
| `running` | Worker processing task |
| `success` | Task completed, video ready |
| `failed` | Task failed, check error field |

## Common HTTP Status Codes

| Code | Meaning | Common Cause |
|------|---------|--------------|
| 200 | OK | Request successful |
| 201 | Created | Task created successfully |
| 400 | Bad Request | Invalid parameters or URL expired |
| 404 | Not Found | Task or video not found |
| 413 | Payload Too Large | File exceeds 100MB limit |
| 500 | Server Error | Internal error |

## File Size Limits

| Operation | Per File | Total |
|-----------|----------|-------|
| Caption | 100MB | 100MB |
| Background Music | 100MB each | 200MB |
| Merge | 100MB each | 500MB |

## Whisper Models

| Model | Speed | Accuracy | Use Case |
|-------|-------|----------|----------|
| tiny | ⚡⚡⚡⚡⚡ | ⭐⭐ | Testing |
| base | ⚡⚡⚡⚡ | ⭐⭐⭐ | Simple speech |
| small | ⚡⚡⚡ | ⭐⭐⭐⭐ | General use (default) |
| medium | ⚡⚡ | ⭐⭐⭐⭐⭐ | Noisy audio |
| large | ⚡ | ⭐⭐⭐⭐⭐ | Professional |

## Processing Times

| Task | Typical Duration |
|------|------------------|
| Caption (small) | 1-3 minutes |
| Caption (large) | 3-8 minutes |
| Merge (2 scenes) | 2-5 minutes |
| Background Music | 30 sec - 2 min |

## Error Handling

### URL Expired (403 Forbidden)
```json
{
  "detail": "Access denied (403 Forbidden). The URL may have expired or requires authentication."
}
```

**Solution:** Generate fresh URL with longer expiration (30+ minutes)

### File Too Large (413)
```json
{
  "detail": "File size 150.5MB exceeds limit of 100MB"
}
```

**Solution:** Compress video or split into segments

### Task Not Found (404)
```json
{
  "detail": "Task not found"
}
```

**Solution:** Check task_id or task may have expired (>2 hours)

## URL Requirements

✅ **Valid URLs:**
```
https://cdn.example.com/video.mp4
https://storage.example.com/video.mp4?Expires=9999999999&Signature=abc
```

❌ **Invalid URLs:**
```
https://storage.example.com/video.mp4?Expires=1234567890  # Expired
https://internal-server.local/video.mp4  # Not accessible
```

## Polling Best Practices

```python
import time
import requests

def poll_until_complete(task_id, interval=5, timeout=600):
    start = time.time()
    while time.time() - start < timeout:
        response = requests.get(f"https://fantastic-endurance-production.up.railway.app/tasks/{task_id}")
        status = response.json()["status"]

        if status == "success":
            return response.json()["video_url"]
        elif status == "failed":
            raise Exception(response.json()["error"])

        time.sleep(interval)

    raise TimeoutError("Task exceeded timeout")
```

## Video Expiration

⏰ **Videos expire 2 hours after completion**
- Download promptly after processing
- Automatic cleanup runs hourly
- No extension available

## Health Check

```bash
curl "https://fantastic-endurance-production.up.railway.app/health"
```

```json
{
  "status": "healthy",
  "redis": "connected",
  "supabase": "connected",
  "queue_length": 3
}
```

## Interactive Documentation

📚 **Swagger UI:** https://fantastic-endurance-production.up.railway.app/docs
📖 **ReDoc:** https://fantastic-endurance-production.up.railway.app/redoc

## Format Support

**Video:** MP4, MOV, AVI, MKV, WebM
**Audio:** MP3, WAV, AAC, M4A, FLAC

**Recommended:**
- Video: MP4 (H.264 + AAC)
- Audio: MP3 or AAC

## Common Dimensions

| Format | Width × Height | Use Case |
|--------|----------------|----------|
| Portrait | 1080 × 1920 | Instagram Stories, TikTok |
| Landscape | 1920 × 1080 | YouTube, general video |
| Square | 1080 × 1080 | Instagram Feed |
| HD | 1280 × 720 | Web video |
| 4K | 3840 × 2160 | High quality |

## Volume Levels

**Background Music:**
- Default: 0.3 (30%)
- Range: 0.0 - 1.0
- Quiet: 0.15
- Moderate: 0.3
- Loud: 0.6

**Video Volume:**
- Default: 1.0 (100%)
- Range: 0.0 - 1.0
- Muted: 0.0
- Half: 0.5
- Full: 1.0

**Voiceover Volume:**
- Default: 2.0 (200%)
- Range: 0.0 - 10.0
- Quiet: 1.0
- Normal: 2.0
- Loud: 3.0

## Troubleshooting

**Worker not processing?**
```bash
curl "https://fantastic-endurance-production.up.railway.app/debug/queue"
```

**Video not found?**
- Check status is "success"
- Verify video hasn't expired (>2 hours)
- Check filename matches pattern

**Slow processing?**
- Use smaller Whisper model (tiny, base)
- Check queue length
- Consider shorter videos

**Out of memory?**
- Use smaller Whisper model
- Reduce concurrent tasks
- Process shorter videos

## Support

- 📚 Full Documentation: [API_DOCS.md](./API_DOCS.md)
- 🏗️ Architecture: [ARCHITECTURE.md](./ARCHITECTURE.md)
- 🚀 Deployment: [DEPLOYMENT.md](./DEPLOYMENT.md)
- 🔗 URL Handling: [URL_HANDLING.md](./URL_HANDLING.md)

## One-Liner Examples

**Complete workflow in one command:**
```bash
TASK=$(curl -s -X POST "https://fantastic-endurance-production.up.railway.app/tasks/caption" \
  -H "Content-Type: application/json" \
  -d '{"video_url":"https://example.com/video.mp4"}' \
  | jq -r '.task_id') && \
while true; do
  STATUS=$(curl -s "https://fantastic-endurance-production.up.railway.app/tasks/$TASK" | jq -r '.status')
  echo "Status: $STATUS"
  [[ "$STATUS" == "success" ]] && break
  sleep 5
done && \
curl -s "https://fantastic-endurance-production.up.railway.app/tasks/$TASK" | jq -r '.video_url' | xargs curl -o output.mp4
```

**Quick health check:**
```bash
curl -s "https://fantastic-endurance-production.up.railway.app/health" | jq
```

**Check queue status:**
```bash
curl -s "https://fantastic-endurance-production.up.railway.app/debug/queue" | jq
```
