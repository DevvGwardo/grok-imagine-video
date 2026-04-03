# API Reference

## GrokImagineVideoClient

```python
from grok_video_api import GrokImagineVideoClient

client = GrokImagineVideoClient(api_key="your-xai-api-key")
```

### Constructor

```python
GrokImagineVideoClient(
    api_key: str,
    base_url: str = "https://api.x.ai/v1"
)
```

---

## Image Methods

### `generate_image()`

Generate images from a text prompt.

```python
client.generate_image(
    prompt: str,                # Required — be descriptive
    n: int = 1,                # 1-10 variations
    aspect_ratio: str = "1:1",  # 16:9, 9:16, 1:1, 4:3, 3:4, 3:2, 2:3
    response_format: str = "url"  # "url" or "b64_json"
) -> {"data": [{"url": "...", ...}]}
```

**Returns:** A dict containing an array of generated images.

---

### `edit_image()`

Edit an existing image via natural language.

```python
client.edit_image(
    image_url: str,             # Public URL or base64 data URI
    prompt: str,                # Required — natural language instruction
    n: int = 1,                # 1-10 variations
    response_format: str = "url"  # "url" or "b64_json"
) -> {"data": [{"url": "...", ...}]}
```

---

### `download_image()`

```python
client.download_image(
    image_url: str,
    output_path: str    # Local path to save the image
) -> str    # Returns the output_path
```

---

## Video Methods

### `text_to_video()`

Create a video from a text description. Returns immediately with a `request_id` — poll with `wait_for_completion()`.

```python
client.text_to_video(
    prompt: str,                # Required — specific, include camera direction
    duration: int = 10,         # 1-15 seconds
    aspect_ratio: str = "16:9",
    resolution: str = "480p"     # 480p (fast) or 720p (quality)
) -> {"request_id": "vid_..."}
```

---

### `image_to_video()`

Animate a static image into a video.

```python
client.image_to_video(
    image_url: str,             # Public URL or base64 data URI
    prompt: str = "",            # Optional — guide the animation
    duration: int = 10          # 1-15 seconds
) -> {"request_id": "vid_..."}
```

---

### `edit_video()`

Edit an existing video via natural language.

```python
client.edit_video(
    video_url: str,             # Public URL of source video
    edit_prompt: str             # Natural language instruction
) -> {"request_id": "vid_..."}
```

---

### `get_job_status()`

Check if a video generation job is complete.

```python
client.get_job_status(request_id: str) -> {
    "status": "pending",        # if still running
    "video": {"url": "..."}     # if complete
}
```

---

### `wait_for_completion()`

Poll `get_job_status()` until the job finishes or times out.

```python
client.wait_for_completion(
    request_id: str,
    poll_interval: int = 10,     # seconds between checks
    timeout: int = 600,          # max seconds to wait
    progress_callback: callable = None
) -> {"video": {"url": "..."}}
```

---

### `download_video()`

```python
client.download_video(
    response_data: Dict,     # Response from wait_for_completion / get_job_status
    output_path: str         # Local path to save the video
) -> str    # Returns the output_path
```

---

### `generate_long_video()`

Generate videos longer than 15s by splitting into segments and stitching with ffmpeg.

```python
client.generate_long_video(
    prompt: str,
    total_duration: int,            # Any length
    aspect_ratio: str = "16:9",
    resolution: str = "480p",
    output_dir: str = "/tmp",
    segment_duration: int = 15,     # 1-15 seconds per segment
    poll_interval: int = 10,
    timeout: int = 600,
    progress_callback: callable = None
) -> List[str]    # Ordered list of segment file paths
```

---

### `concatenate_segments()`

Join video segments from `generate_long_video()` into a single file using ffmpeg.

```python
client.concatenate_segments(
    segment_paths: List[str],   # Ordered list from generate_long_video()
    output_path: str            # Final output file path
) -> str    # Returns the output_path
```

---

## Parameters Summary

### Image Generation

| Parameter | Default | Range |
|-----------|---------|-------|
| `prompt` | required | — |
| `n` | 1 | 1-10 |
| `aspect_ratio` | 1:1 | 16:9, 9:16, 1:1, 4:3, 3:4, 3:2, 2:3 |
| `response_format` | url | url, b64_json |

### Video Generation

| Parameter | Default | Range |
|-----------|---------|-------|
| `prompt` | required | — |
| `duration` | 10 | 1-15 seconds |
| `aspect_ratio` | 16:9 | same as image |
| `resolution` | 480p | 480p, 720p |

### Long Video

| Parameter | Default | Range |
|-----------|---------|-------|
| `total_duration` | required | unlimited |
| `segment_duration` | 15 | 1-15 seconds |
| `resolution` | 480p | 480p, 720p |
| `timeout` | 600 | seconds |
| `poll_interval` | 10 | seconds |

## Error Types

| Exception | Cause |
|-----------|-------|
| `HTTPError (401)` | Invalid or missing API key |
| `HTTPError (429)` | Rate limit exceeded — retry after waiting |
| `HTTPError (400)` | Content policy violation — rephrase prompt |
| `TimeoutError` | Job didn't complete within timeout |
| `FileNotFoundError` | ffmpeg missing or segment file not found |
| `RuntimeError` | Segment expired during long video generation |
