# Grok Imagine Video & Image

A Python client and [OpenClaw](https://docs.openclaw.ai) skill for generating images and videos using [xAI's Grok Imagine APIs](https://docs.x.ai/developers/model-capabilities).

## Features

- **Text-to-Image** — Generate images from natural language descriptions (up to 10 variations)
- **Image Editing** — Edit existing images with natural language instructions
- **Text-to-Video** — Generate video clips from natural language descriptions
- **Image-to-Video** — Animate static images into motion video
- **Video Editing** — Edit existing videos with natural language instructions (filters, speed, color grading, effects)
- **Async Polling** — Non-blocking video job management with progress callbacks
- **OpenClaw Integration** — Works as a drop-in skill for Discord, Telegram, and WhatsApp bots

## Quick Start

### 1. Get an API Key

Sign up at [console.x.ai](https://console.x.ai/) and grab your API key.

### 2. Set Your Key

```bash
export XAI_API_KEY="your-key-here"
```

### 3. Use the Client

```python
from scripts.grok_video_api import GrokImagineVideoClient

client = GrokImagineVideoClient(api_key="your-key")

# Generate an image from text
result = client.generate_image("A cyberpunk cityscape at night, neon lights reflecting on wet streets")
print(result)  # Contains image URL or base64 data

# Generate a video from text
result = client.text_to_video("A golden retriever running through a sunny meadow", duration=10)

# Wait for it to finish (takes 1-3 minutes)
final = client.wait_for_completion(result["request_id"])

# Download the result
client.download_video(final, "output.mp4")
```

## Usage

### Image Generation

```python
# Generate a single image
result = client.generate_image(
    prompt="A collage of London landmarks in a stenciled street-art style",
    aspect_ratio="16:9"
)

# Generate multiple variations
result = client.generate_image(
    prompt="A futuristic city skyline at night",
    n=4,                      # Up to 10 variations
    aspect_ratio="16:9"
)

# Get base64 output instead of a URL
result = client.generate_image(
    prompt="A watercolor painting of a mountain lake",
    response_format="b64_json"
)
```

### Image Editing

```python
result = client.edit_image(
    image_url="https://example.com/photo.jpg",
    prompt="Change the sky to a dramatic sunset"
)

# Edit with a base64 source image
result = client.edit_image(
    image_url=f"data:image/jpeg;base64,{image_data}",
    prompt="Make it look like a watercolor painting"
)
```

### Text-to-Video

```python
result = client.text_to_video(
    prompt="Slow pan across a cyberpunk cityscape at night",
    duration=10,          # 1-15 seconds
    aspect_ratio="16:9",  # 16:9, 9:16, 1:1, 4:3, 3:4, 3:2, 2:3
    resolution="720p"     # 480p (faster) or 720p (higher quality)
)
```

### Image-to-Video

```python
result = client.image_to_video(
    image_url="https://example.com/landscape.jpg",
    prompt="Make the clouds drift slowly across the sky",
    duration=10
)
```

### Video Editing

```python
result = client.edit_video(
    video_url="https://example.com/clip.mp4",
    edit_prompt="Add a warm sunset filter and slow down to 50% speed"
)
```

### Polling & Download

```python
# Poll with a progress callback
final = client.wait_for_completion(
    result["request_id"],
    poll_interval=10,   # seconds between checks
    timeout=600,        # max wait time
    progress_callback=lambda r: print("Done!" if "video" in r else "Pending...")
)

# Download the finished video
client.download_video(final, "my_video.mp4")
```

### Standalone Script

```bash
python scripts/grok_video_api.py
```

Edit the `mode` variable in `main()` to switch between text-to-video, image-to-video, and editing modes.

## OpenClaw Skill Installation

To use this as an OpenClaw chatbot skill:

```bash
mkdir -p ~/.openclaw/skills
cp grok-imagine-video.skill ~/.openclaw/skills/
cd ~/.openclaw/skills && unzip grok-imagine-video.skill
openclaw gateway restart
```

Then tell your bot things like:

> "Generate an image of a cyberpunk cityscape at night"
> "Edit this image — make it look like a watercolor painting"
> "Generate a video of a sunset over the ocean"
> "Animate this image — make the clouds move"
> "Edit this video — add a warm sunset filter"

## API Limits

| Constraint | Value |
|---|---|
| Images per request | 1–10 |
| Video duration | 1–15 seconds |
| Video editing input limit | 8.7 seconds |
| Video resolution | 480p or 720p |
| Rate limit | 60 requests/min |
| Concurrent jobs | 15 per account |

Image and video URLs are **temporary** — download promptly after generation.

## Prompt Tips

### Images
- Be descriptive: *"A collage of London landmarks in a stenciled street-art style"*
- Specify style: *"Watercolor painting of a mountain lake at dawn"*
- Use multiple variations (`n=4`) to explore different interpretations

### Videos
- Be specific: *"A golden retriever running through a sunny meadow"*
- Include camera direction: *"Slow pan from left to right over a mountain range"*
- Specify lighting: *"Warm golden hour lighting with long shadows"*
- Use 480p for fast iteration, 720p for final renders

## Project Structure

```
grok-imagine-video/
├── scripts/
│   └── grok_video_api.py      # Python client library
├── references/
│   └── api_reference.md       # Full API documentation
├── SKILL.md                   # OpenClaw skill definition
├── CHANGELOG.md               # Version history
└── README.md
```

## Requirements

- Python 3.8+
- [`requests`](https://pypi.org/project/requests/) library
- xAI API key ([console.x.ai](https://console.x.ai/))
- [OpenClaw](https://docs.openclaw.ai) (only for chatbot integration)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=DevvGwardo/grok-imagine-video&type=Date)](https://star-history.com/#DevvGwardo/grok-imagine-video&Date)

## License

MIT
