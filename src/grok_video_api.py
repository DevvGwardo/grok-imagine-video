#!/usr/bin/env python3
"""
xAI Grok Imagine Video API Client
Handles text-to-video, image-to-video, image generation, and video editing via natural language.
"""

import math
import os
import subprocess
import tempfile
import time
import json
import requests
from typing import List, Optional, Dict, Any, Callable


class GrokImagineVideoClient:
    """Python client for xAI Grok Imagine API."""

    def __init__(self, api_key: str, base_url: str = "https://api.x.ai/v1"):
        """
        Initialize the client.

        Args:
            api_key: xAI API key from environment or config.
            base_url: API base URL (default: https://api.x.ai/v1).
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    # ─── Image Methods ───────────────────────────────────────────────────────

    def generate_image(
        self,
        prompt: str,
        n: int = 1,
        aspect_ratio: str = "1:1",
        response_format: str = "url"
    ) -> Dict[str, Any]:
        """
        Generate images from a text prompt.

        Args:
            prompt: Text description of the image to generate.
            n: Number of image variations (1-10).
            aspect_ratio: Aspect ratio of the output. Options: 1:1, 16:9, 9:16,
                4:3, 3:4, 3:2, 2:3. Default: 1:1.
            response_format: "url" for a temporary URL, or "b64_json" for
                base64-encoded JSON. Default: "url".

        Returns:
            API response containing generated image URL(s) or base64 data.
        """
        url = f"{self.base_url}/images/generations"
        payload = {
            "model": "grok-imagine-image",
            "prompt": prompt,
            "n": n,
            "aspect_ratio": aspect_ratio,
            "response_format": response_format
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def edit_image(
        self,
        image_url: str,
        prompt: str,
        n: int = 1,
        response_format: str = "url"
    ) -> Dict[str, Any]:
        """
        Edit an existing image via natural language instruction.

        Args:
            image_url: Public URL or base64 data URI of the source image.
            prompt: Natural language instruction for the edit.
            n: Number of variations (1-10). Default: 1.
            response_format: "url" or "b64_json". Default: "url".

        Returns:
            API response with edited image URL(s) or base64 data.
        """
        url = f"{self.base_url}/images/edits"
        payload = {
            "model": "grok-imagine-image",
            "prompt": prompt,
            "image": {"url": image_url, "type": "image_url"},
            "n": n,
            "response_format": response_format
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def download_image(self, image_url: str, output_path: str) -> str:
        """
        Download a generated image to a local file.

        Args:
            image_url: URL of the generated image.
            output_path: Local path to save the image.

        Returns:
            The output_path that was written.
        """
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return output_path

    # ─── Video Methods ──────────────────────────────────────────────────────

    def text_to_video(
        self,
        prompt: str,
        duration: int = 10,
        aspect_ratio: str = "16:9",
        resolution: str = "480p"
    ) -> Dict[str, Any]:
        """
        Generate a video from a text description.

        The job runs asynchronously. Call wait_for_completion() with the
        returned request_id to poll until the video is ready.

        Args:
            prompt: Text description of the video to generate. Be specific
                and include camera direction for best results.
            duration: Video duration in seconds (1-15). Default: 10.
            aspect_ratio: Aspect ratio. Options: 16:9, 9:16, 1:1, 4:3, 3:4,
                3:2, 2:3. Default: 16:9.
            resolution: "480p" for faster generation, "720p" for higher
                quality. Default: 480p.

        Returns:
            API response containing {"request_id": "vid_..."}.
        """
        url = f"{self.base_url}/videos/generations"
        payload = {
            "model": "grok-imagine-video",
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def image_to_video(
        self,
        image_url: str,
        prompt: str = "",
        duration: int = 10
    ) -> Dict[str, Any]:
        """
        Animate a static image into a video.

        Args:
            image_url: Public URL or base64 data URI of the source image.
            prompt: Optional text prompt to guide the animation.
            duration: Video duration in seconds (1-15). Default: 10.

        Returns:
            API response containing {"request_id": "vid_..."}.
        """
        url = f"{self.base_url}/videos/generations"
        payload = {
            "model": "grok-imagine-video",
            "prompt": prompt,
            "image": {"url": image_url},
            "duration": duration
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def edit_video(
        self,
        video_url: str,
        edit_prompt: str
    ) -> Dict[str, Any]:
        """
        Edit an existing video via natural language instruction.

        Args:
            video_url: Public URL of the source video.
            edit_prompt: Natural language instruction describing the edit
                (e.g. "Add a warm sunset filter and slow to 50% speed").

        Returns:
            API response containing {"request_id": "vid_..."}.
        """
        url = f"{self.base_url}/videos/generations"
        payload = {
            "model": "grok-imagine-video",
            "prompt": edit_prompt,
            "video_url": video_url
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def get_job_status(self, request_id: str) -> Dict[str, Any]:
        """
        Check the status of a video generation job.

        Args:
            request_id: The request ID returned from text_to_video(),
                image_to_video(), or edit_video().

        Returns:
            {"status": "pending"} if still running, or
            {"video": {"url": "..."}} if complete.
        """
        url = f"{self.base_url}/videos/{request_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def wait_for_completion(
        self,
        request_id: str,
        poll_interval: int = 10,
        timeout: int = 600,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        Poll job status until completion or timeout.

        Args:
            request_id: The request ID to poll.
            poll_interval: Seconds between status checks. Default: 10.
            timeout: Maximum seconds to wait before raising TimeoutError.
                Default: 600 (10 minutes).
            progress_callback: Optional callable invoked on each poll with
                the current status response.

        Returns:
            Final response dict containing {"video": {"url": "..."}}.

        Raises:
            TimeoutError: If the job does not complete within the timeout.
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            response = self.get_job_status(request_id)

            if progress_callback:
                progress_callback(response)

            if "video" in response and response["video"].get("url"):
                return response

            time.sleep(poll_interval)

        raise TimeoutError(
            f"Request {request_id} timed out after {timeout} seconds"
        )

    def download_video(
        self,
        response_data: Dict[str, Any],
        output_path: str
    ) -> str:
        """
        Download a completed video to a local file.

        Args:
            response_data: Response from wait_for_completion() or
                get_job_status() containing the video URL.
            output_path: Local path to save the video.

        Returns:
            The output_path that was written.
        """
        video_url = response_data.get("video", {}).get("url")
        if not video_url:
            raise ValueError("No video URL in response_data")

        response = requests.get(video_url, stream=True)
        response.raise_for_status()

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return output_path

    # ─── Long Video ─────────────────────────────────────────────────────────

    def generate_long_video(
        self,
        prompt: str,
        total_duration: int,
        aspect_ratio: str = "16:9",
        resolution: str = "480p",
        output_dir: str = "/tmp",
        segment_duration: int = 15,
        poll_interval: int = 10,
        timeout: int = 600,
        progress_callback: Optional[
            Callable[[int, int, str], None]
        ] = None
    ) -> List[str]:
        """
        Generate a video longer than 15 seconds via segmentation.

        Submits concurrent API calls for each segment and polls until all
        complete, then returns the ordered list of local segment paths.

        Args:
            prompt: Text description of the video.
            total_duration: Total desired duration in seconds (unlimited).
            aspect_ratio: Aspect ratio. Default: 16:9.
            resolution: "480p" or "720p". Default: 480p.
            output_dir: Directory to save downloaded segment files.
                Default: "/tmp".
            segment_duration: Maximum seconds per API call (1-15).
                Default: 15.
            poll_interval: Seconds between status checks. Default: 10.
            timeout: Maximum seconds to wait for all segments. Default: 600.
            progress_callback: Optional callable invoked with
                (segment_index, total_segments, status) on each update.

        Returns:
            Ordered list of local file paths for each segment.

        Raises:
            ValueError: If segment_duration is outside 1-15.
            TimeoutError: If segments do not complete within timeout.
            RuntimeError: If a segment expires before completion.
        """
        if not 1 <= segment_duration <= 15:
            raise ValueError("segment_duration must be between 1 and 15")

        n_segments = math.ceil(total_duration / segment_duration)
        durations = []
        remaining = total_duration
        for _ in range(n_segments):
            seg = min(segment_duration, remaining)
            durations.append(seg)
            remaining -= seg

        # Submit all segment jobs concurrently
        request_ids = []
        for i, dur in enumerate(durations):
            result = self.text_to_video(
                prompt=prompt,
                duration=dur,
                aspect_ratio=aspect_ratio,
                resolution=resolution
            )
            request_ids.append(result["request_id"])
            if progress_callback:
                progress_callback(i, n_segments, "submitted")

        # Poll all pending jobs to completion
        os.makedirs(output_dir, exist_ok=True)
        segment_paths: List[Optional[str]] = [None] * n_segments
        pending = list(range(n_segments))
        start_time = time.time()

        while pending and time.time() - start_time < timeout:
            still_pending = []
            for idx in pending:
                response = self.get_job_status(request_ids[idx])
                if "video" in response and response["video"].get("url"):
                    path = os.path.join(output_dir, f"segment_{idx:04d}.mp4")
                    self.download_video(response, path)
                    segment_paths[idx] = path
                    if progress_callback:
                        progress_callback(idx, n_segments, "done")
                elif response.get("status") == "expired":
                    raise RuntimeError(
                        f"Segment {idx} expired before completion"
                    )
                else:
                    still_pending.append(idx)
            pending = still_pending
            if pending:
                time.sleep(poll_interval)

        if pending:
            raise TimeoutError(
                f"Segments {pending} did not complete within {timeout}s"
            )

        return segment_paths

    def concatenate_segments(
        self,
        segment_paths: List[str],
        output_path: str
    ) -> str:
        """
        Concatenate video segments into a single file using ffmpeg.

        Requires ffmpeg to be installed and accessible in PATH.

        Args:
            segment_paths: Ordered list of local segment file paths, as
                returned by generate_long_video().
            output_path: Local path for the final concatenated video.

        Returns:
            The output_path that was written.

        Raises:
            FileNotFoundError: If ffmpeg is missing or a segment file
                does not exist.
            RuntimeError: If ffmpeg fails during concatenation.
        """
        for path in segment_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Segment not found: {path}")

        out_dir = os.path.dirname(os.path.abspath(output_path))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            concat_list = f.name
            for path in segment_paths:
                f.write(f"file '{os.path.abspath(path)}'\n")

        try:
            result = subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-f", "concat",
                    "-safe", "0",
                    "-i", concat_list,
                    "-c", "copy",
                    output_path
                ],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise RuntimeError(f"ffmpeg failed:\n{result.stderr}")
        finally:
            os.unlink(concat_list)

        return output_path
