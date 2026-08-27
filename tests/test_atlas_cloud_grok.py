"""Focused tests for the optional Atlas Cloud Grok Imagine backend."""

from unittest.mock import MagicMock, patch

import pytest

from scripts.atlas_cloud_grok import AtlasCloudGrokClient


@pytest.fixture
def client():
    return AtlasCloudGrokClient("test-api-key")


def atlas_response(data):
    response = MagicMock()
    response.json.return_value = {"code": 200, "data": data}
    return response


class TestSingleSubmit:
    def test_text_to_video_uses_atlas_schema(self, client):
        with patch("scripts.atlas_cloud_grok.requests.post") as post:
            post.return_value = atlas_response({"id": "video-1", "status": "created"})
            result = client.text_to_video(
                "A slow orbit around a glass sculpture",
                duration=6,
                aspect_ratio="9:16",
                resolution="720p",
            )

        assert result["request_id"] == "video-1"
        post.assert_called_once()
        assert post.call_args.kwargs["json"] == {
            "model": "xai/grok-imagine-video-v1.5/text-to-video",
            "prompt": "A slow orbit around a glass sculpture",
            "duration": 6,
            "aspect_ratio": "9:16",
            "resolution": "720p",
        }

    def test_image_generation_uses_num_images(self, client):
        with patch("scripts.atlas_cloud_grok.requests.post") as post:
            post.return_value = atlas_response({"id": "image-1"})
            client.generate_image("A neon skyline", n=2, quality="low")

        post.assert_called_once()
        payload = post.call_args.kwargs["json"]
        assert payload["num_images"] == 2
        assert payload["quality"] == "low"

    def test_image_edit_uses_image_urls(self, client):
        with patch("scripts.atlas_cloud_grok.requests.post") as post:
            post.return_value = atlas_response({"id": "edit-1"})
            client.edit_image("https://example.com/source.png", "Make it cinematic")

        assert post.call_args.kwargs["json"]["image_urls"] == [
            "https://example.com/source.png"
        ]

    def test_image_to_video_uses_image_url(self, client):
        with patch("scripts.atlas_cloud_grok.requests.post") as post:
            post.return_value = atlas_response({"id": "i2v-1"})
            client.image_to_video(
                "https://example.com/source.png", prompt="Drifting clouds"
            )

        assert post.call_args.kwargs["json"]["image_url"] == (
            "https://example.com/source.png"
        )

    def test_video_edit_uses_edit_model(self, client):
        with patch("scripts.atlas_cloud_grok.requests.post") as post:
            post.return_value = atlas_response({"id": "edit-video-1"})
            client.edit_video("https://example.com/source.mp4", "Use dusk lighting")

        assert post.call_args.kwargs["json"]["model"] == (
            "xai/grok-imagine-video/edit-video"
        )


class TestPolling:
    def test_wait_polls_get_until_completed(self, client):
        with patch.object(client, "get_job_status") as get_status:
            get_status.side_effect = [
                {"status": "processing", "outputs": []},
                {"status": "completed", "outputs": ["https://example.com/out.mp4"]},
            ]
            with patch("scripts.atlas_cloud_grok.time.sleep"):
                result = client.wait_for_completion("video-1", poll_interval=1)

        assert result["outputs"] == ["https://example.com/out.mp4"]
        assert get_status.call_count == 2

    def test_failed_job_stops_polling(self, client):
        with patch.object(client, "get_job_status") as get_status:
            get_status.return_value = {"status": "failed", "message": "bad input"}
            with pytest.raises(RuntimeError, match="bad input"):
                client.wait_for_completion("video-1")

        get_status.assert_called_once_with("video-1")
