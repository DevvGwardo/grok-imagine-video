#!/usr/bin/env python3
"""Atlas Cloud client for Grok Imagine image and video models."""

import os
import time
from typing import Any, Callable, Dict, Optional

import requests


class AtlasCloudGrokClient:
    """Submit Grok Imagine jobs through the optional Atlas Cloud backend."""

    IMAGE_MODEL = "xai/grok-imagine-image-2.0/text-to-image"
    IMAGE_EDIT_MODEL = "xai/grok-imagine-image-2.0/edit"
    VIDEO_MODEL = "xai/grok-imagine-video-v1.5/text-to-video"
    IMAGE_TO_VIDEO_MODEL = "xai/grok-imagine-video-v1.5/image-to-video"
    VIDEO_EDIT_MODEL = "xai/grok-imagine-video/edit-video"

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.atlascloud.ai/api/v1",
        request_timeout: int = 120,
    ):
        if not api_key:
            raise ValueError("ATLASCLOUD_API_KEY is required")
        self.base_url = base_url.rstrip("/")
        self.request_timeout = request_timeout
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "grok-imagine-video/atlas-cloud",
        }

    @staticmethod
    def _unwrap(payload: Dict[str, Any]) -> Dict[str, Any]:
        code = payload.get("code")
        if code not in (None, 0, 200):
            raise RuntimeError(payload.get("message") or f"Atlas Cloud error {code}")
        data = payload.get("data", payload)
        if not isinstance(data, dict):
            raise RuntimeError("Atlas Cloud returned an invalid response body")
        return data

    def _submit(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Generation POSTs are deliberately single-attempt. Callers must not retry
        # because an accepted request may already be billable.
        response = requests.post(
            f"{self.base_url}/{endpoint}",
            headers=self.headers,
            json=payload,
            timeout=self.request_timeout,
        )
        response.raise_for_status()
        data = self._unwrap(response.json())
        request_id = data.get("id") or data.get("request_id")
        if not request_id:
            raise RuntimeError("Atlas Cloud response did not include a request id")
        result = dict(data)
        result["request_id"] = request_id
        return result

    def generate_image(
        self,
        prompt: str,
        n: int = 1,
        aspect_ratio: str = "1:1",
        resolution: str = "1k",
        quality: str = "medium",
        model: str = IMAGE_MODEL,
    ) -> Dict[str, Any]:
        return self._submit(
            "model/generateImage",
            {
                "model": model,
                "prompt": prompt,
                "num_images": n,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
                "quality": quality,
            },
        )

    def edit_image(
        self,
        image_url: str,
        prompt: str,
        n: int = 1,
        aspect_ratio: str = "auto",
        resolution: str = "1k",
        quality: str = "medium",
        model: str = IMAGE_EDIT_MODEL,
    ) -> Dict[str, Any]:
        return self._submit(
            "model/generateImage",
            {
                "model": model,
                "prompt": prompt,
                "image_urls": [image_url],
                "num_images": n,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
                "quality": quality,
            },
        )

    def text_to_video(
        self,
        prompt: str,
        duration: int = 10,
        aspect_ratio: str = "16:9",
        resolution: str = "480p",
        model: str = VIDEO_MODEL,
    ) -> Dict[str, Any]:
        return self._submit(
            "model/generateVideo",
            {
                "model": model,
                "prompt": prompt,
                "duration": duration,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
            },
        )

    def image_to_video(
        self,
        image_url: str,
        prompt: str = "",
        duration: int = 10,
        aspect_ratio: str = "16:9",
        resolution: str = "480p",
        model: str = IMAGE_TO_VIDEO_MODEL,
    ) -> Dict[str, Any]:
        return self._submit(
            "model/generateVideo",
            {
                "model": model,
                "prompt": prompt,
                "image_url": image_url,
                "duration": duration,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
            },
        )

    def edit_video(
        self,
        video_url: str,
        edit_prompt: str,
        model: str = VIDEO_EDIT_MODEL,
    ) -> Dict[str, Any]:
        return self._submit(
            "model/generateVideo",
            {"model": model, "prompt": edit_prompt, "video_url": video_url},
        )

    def get_job_status(self, request_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/model/prediction/{request_id}",
            headers=self.headers,
            timeout=self.request_timeout,
        )
        response.raise_for_status()
        return self._unwrap(response.json())

    def wait_for_completion(
        self,
        request_id: str,
        poll_interval: int = 5,
        timeout: int = 600,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        deadline = time.monotonic() + timeout
        while True:
            result = self.get_job_status(request_id)
            if progress_callback:
                progress_callback(result)

            status = str(result.get("status", "")).lower()
            if status in {"completed", "succeeded"}:
                return result
            if status in {"failed", "canceled", "cancelled"}:
                raise RuntimeError(
                    result.get("error")
                    or result.get("message")
                    or f"Atlas Cloud request {request_id} {status}"
                )
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(
                    f"Request {request_id} timed out after {timeout} seconds"
                )
            time.sleep(min(poll_interval, remaining))

    def download_output(
        self, response_data: Dict[str, Any], output_path: str, index: int = 0
    ) -> str:
        outputs = response_data.get("outputs") or []
        if index >= len(outputs):
            raise ValueError("No Atlas Cloud output URL at the requested index")
        response = requests.get(
            outputs[index], stream=True, timeout=self.request_timeout
        )
        response.raise_for_status()
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "wb") as output_file:
            for chunk in response.iter_content(chunk_size=8192):
                output_file.write(chunk)
        return output_path
