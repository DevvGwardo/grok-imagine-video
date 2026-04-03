# Grok Imagine Video

Python client for xAI's Grok Imagine API — generate, edit, and animate images and videos via natural language.

## Installation

```bash
pip install requests
```

Or with uv:

```bash
uv pip install requests
```

Or install from source:

```bash
git clone https://github.com/DevvGwardo/grok-imagine-video.git
cd grok-imagine-video
pip install -e .
```

## Quick Start

```python
import os
from grok_video_api import GrokImagineVideoClient

client = GrokImagineVideoClient(os.getenv("XAI_API_KEY"))

# Generate an image (instant)
img = client.generate_image("A cyberpunk cityscape at night")
print(img["data"][0]["url"])

# Create a video (~2-3 min, async)
job = client.text_to_video(
    prompt="A golden retriever running through a sunny meadow",
    duration=10,
    resolution="720p"
)
result = client.wait_for_completion(job["request_id"])
client.download_video(result, "output.mp4")
```

## Configuration

**Required:** `XAI_API_KEY` from [console.x.ai](https://console.x.ai)

The client reads the key from the `XAI_API_KEY` environment variable by default. You can also pass it directly:

```python
client = GrokImagineVideoClient("xai-your-key-here")
```

## Capabilities

| Feature | Description | Latency |
|---------|-------------|---------|
| Text-to-image | Generate images from text prompts | Instant |
| Image editing | Edit images via natural language | Instant |
| Text-to-video | Create videos from text descriptions | ~2-3 min |
| Image-to-video | Animate a static image | ~2-3 min |
| Video editing | Edit videos via natural language | ~2-3 min |
| Long video | Videos longer than 15s via segmentation | Scales with length |

## API Reference

### Image Generation

```python
client.generate_image(
    prompt="A serene mountain lake at golden hour",
    n=4,                    # 1-10 variations
    aspect_ratio="16:9",    # 16:9, 9:16, 1:1, 4:3, 3:4, 3:2, 2:3
    response_format="url"    # or "b64_json"
)
```

### Text-to-Video

```python
job = client.text_to_video(
    prompt="Cinematic drone shot over ocean waves at sunset",
    duration=10,            # 1-15 seconds
    aspect_ratio="16:9",
    resolution="720p"      # 480p (fast) or 720p (quality)
)
result = client.wait_for_completion(job["request_id"])
client.download_video(result, "video.mp4")
```

### Image-to-Video

```python
job = client.image_to_video(
    image_url="https://example.com/photo.jpg",
    prompt="Make the clouds drift slowly across the sky",
    duration=10
)
```

### Video Editing

```python
job = client.edit_video(
    video_url="https://example.com/clip.mp4",
    edit_prompt="Add a warm sunset filter and slow to 50% speed"
)
```

### Long Video (beyond 15s)

```python
def progress(idx, total, status):
    print(f"Segment {idx+1}/{total}: {status}")

segments = client.generate_long_video(
    prompt="A cinematic journey through ancient ruins",
    total_duration=60,        # Any length
    segment_duration=15,       # Max 15s per API call
    resolution="720p",
    output_dir="/tmp",
    progress_callback=progress
)
client.concatenate_segments(segments, "long_video.mp4")
```

## Error Handling

```python
from grok_video_api import GrokImagineVideoClient

client = GrokImagineVideoClient(api_key)

try:
    result = client.text_to_video(prompt="A cat playing piano")
    final = client.wait_for_completion(result["request_id"])
except TimeoutError:
    print("Job timed out — try reducing duration")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("Invalid API key")
    elif e.response.status_code == 429:
        print("Rate limited — wait and retry")
    elif e.response.status_code == 400:
        print("Content policy violation — rephrase prompt")
```

## Rate Limits

- 60 requests/minute
- Max 15 concurrent jobs
- Video segments: 1-15 seconds per API call
- Images: 1-10 per request

## Optional Dependencies

`ffmpeg` is required only for long video concatenation:

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

## Testing

```bash
pip install pytest
pytest tests/
```

## License

MIT
