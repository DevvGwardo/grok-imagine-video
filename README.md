# Grok Imagine Video

A Python client and [OpenClaw](https://docs.openclaw.ai) skill for generating, animating, and editing videos using [xAI's Grok Imagine Video API](https://docs.x.ai/developers/model-capabilities/video/generation).

## Features

- **Text-to-Video** — Generate video clips from natural language descriptions
- **Image-to-Video** — Animate static images into motion video
- **Video Editing** — Edit existing videos with natural language instructions (filters, speed, color grading, effects)
- **Async Polling** — Non-blocking job management with progress callbacks
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

# Generate a video from text
result = client.text_to_video("A golden retriever running through a sunny meadow", duration=10)

# Wait for it to finish (takes 1-3 minutes)
final = client.wait_for_completion(result["request_id"])

# Download the result
client.download_video(final, "output.mp4")
```

## Usage

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

> "Generate a video of a sunset over the ocean"
> "Animate this image — make the clouds move"
> "Edit this video — add a warm sunset filter"

## API Limits

| Constraint | Value |
|---|---|
| Video duration | 1–15 seconds |
| Editing input limit | 8.7 seconds |
| Resolution | 480p or 720p |
| Rate limit | 60 requests/min |
| Concurrent jobs | 15 per account |

Video URLs are **temporary** — download promptly after generation.

## Prompt Tips

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
