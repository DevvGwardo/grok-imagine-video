"""
Unit tests for GrokImagineVideoClient.
Run with: pytest tests/
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from src.grok_video_api import GrokImagineVideoClient


@pytest.fixture
def client():
    return GrokImagineVideoClient("test-api-key")


class TestImageGeneration:
    def test_generate_image_returns_data(self, client):
        mock_response = {"data": [{"url": "https://example.com/img.jpg"}]}
        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = MagicMock()
            result = client.generate_image("A sunset over mountains")
            assert "data" in result
            assert len(result["data"]) == 1
            assert result["data"][0]["url"] == "https://example.com/img.jpg"

    def test_generate_image_with_multiple_variations(self, client):
        mock_response = {
            "data": [
                {"url": "https://example.com/img1.jpg"},
                {"url": "https://example.com/img2.jpg"},
            ]
        }
        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = MagicMock()
            result = client.generate_image("A sunset", n=2)
            assert len(result["data"]) == 2

    def test_generate_image_passes_correct_payload(self, client):
        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = {
                "data": [{"url": "https://example.com/img.jpg"}]
            }
            mock_post.return_value.raise_for_status = MagicMock()
            client.generate_image(
                prompt="A mountain lake",
                n=3,
                aspect_ratio="16:9",
                response_format="b64_json"
            )
            call_kwargs = mock_post.call_args[1]
            assert call_kwargs["json"]["prompt"] == "A mountain lake"
            assert call_kwargs["json"]["n"] == 3
            assert call_kwargs["json"]["aspect_ratio"] == "16:9"
            assert call_kwargs["json"]["response_format"] == "b64_json"


class TestImageEditing:
    def test_edit_image_returns_data(self, client):
        mock_response = {"data": [{"url": "https://example.com/edited.jpg"}]}
        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = MagicMock()
            result = client.edit_image(
                image_url="https://example.com/original.jpg",
                prompt="Make it a watercolor"
            )
            assert "data" in result
            assert result["data"][0]["url"] == "https://example.com/edited.jpg"


class TestTextToVideo:
    def test_text_to_video_returns_request_id(self, client):
        mock_response = {"request_id": "vid_abc123"}
        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = MagicMock()
            result = client.text_to_video(prompt="A dog running", duration=10)
            assert result["request_id"] == "vid_abc123"

    def test_text_to_video_passes_correct_payload(self, client):
        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = {"request_id": "vid_test"}
            mock_post.return_value.raise_for_status = MagicMock()
            client.text_to_video(
                prompt="Cinematic ocean waves",
                duration=5,
                aspect_ratio="16:9",
                resolution="720p"
            )
            call_kwargs = mock_post.call_args[1]
            assert call_kwargs["json"]["prompt"] == "Cinematic ocean waves"
            assert call_kwargs["json"]["duration"] == 5
            assert call_kwargs["json"]["aspect_ratio"] == "16:9"
            assert call_kwargs["json"]["resolution"] == "720p"


class TestImageToVideo:
    def test_image_to_video_returns_request_id(self, client):
        mock_response = {"request_id": "vid_img_001"}
        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = MagicMock()
            result = client.image_to_video(
                image_url="https://example.com/photo.jpg",
                prompt="Animate the clouds",
                duration=10
            )
            assert result["request_id"] == "vid_img_001"


class TestVideoEditing:
    def test_edit_video_returns_request_id(self, client):
        mock_response = {"request_id": "vid_edit_001"}
        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status = MagicMock()
            result = client.edit_video(
                video_url="https://example.com/source.mp4",
                edit_prompt="Add a warm filter"
            )
            assert result["request_id"] == "vid_edit_001"


class TestJobStatus:
    def test_get_job_status_pending(self, client):
        mock_response = {"status": "pending", "request_id": "vid_abc123"}
        with patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.raise_for_status = MagicMock()
            result = client.get_job_status("vid_abc123")
            assert result["status"] == "pending"
            assert "video" not in result

    def test_get_job_status_completed(self, client):
        mock_response = {
            "request_id": "vid_abc123",
            "video": {"url": "https://example.com/video.mp4"}
        }
        with patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.raise_for_status = MagicMock()
            result = client.get_job_status("vid_abc123")
            assert "video" in result
            assert result["video"]["url"] == "https://example.com/video.mp4"


class TestWaitForCompletion:
    def test_wait_returns_on_completion(self, client):
        with patch.object(client, "get_job_status") as mock_status:
            mock_status.return_value = {
                "video": {"url": "https://example.com/video.mp4"}
            }
            result = client.wait_for_completion("vid_abc123", poll_interval=1)
            assert "video" in result
            assert mock_status.call_count == 1

    def test_wait_retries_until_done(self, client):
        call_count = [0]
        def fake_status(request_id):
            call_count[0] += 1
            if call_count[0] < 3:
                return {"status": "pending"}
            return {"video": {"url": "https://example.com/video.mp4"}}

        with patch.object(client, "get_job_status", side_effect=fake_status):
            result = client.wait_for_completion("vid_abc123", poll_interval=1)
            assert call_count[0] == 3
            assert "video" in result


class TestLongVideo:
    def test_generate_long_video_segment_count(self, client):
        """60s total with 15s segments = 4 segments"""
        with patch.object(client, "text_to_video") as mock_ttv:
            with patch.object(client, "get_job_status") as mock_status:
                with patch.object(client, "download_video") as mock_dl:
                    mock_ttv.return_value = {"request_id": "vid_seg"}
                    mock_status.return_value = {
                        "video": {"url": "https://example.com/seg.mp4"}
                    }
                    segments = client.generate_long_video(
                        prompt="A journey",
                        total_duration=60,
                        segment_duration=15,
                        output_dir="/tmp",
                        timeout=30
                    )
                    assert len(segments) == 4
                    assert mock_ttv.call_count == 4

    def test_generate_long_video_uneven_segments(self, client):
        """55s total with 15s segments = 4 segments (15+15+15+10)"""
        with patch.object(client, "text_to_video") as mock_ttv:
            with patch.object(client, "get_job_status") as mock_status:
                with patch.object(client, "download_video") as mock_dl:
                    mock_ttv.return_value = {"request_id": "vid_seg"}
                    mock_status.return_value = {
                        "video": {"url": "https://example.com/seg.mp4"}
                    }
                    durations_captured = []
                    def capture_duration(**kwargs):
                        durations_captured.append(kwargs.get("duration"))
                        return {"request_id": "vid_seg"}
                    mock_ttv.side_effect = capture_duration

                    client.generate_long_video(
                        prompt="A journey",
                        total_duration=55,
                        segment_duration=15,
                        output_dir="/tmp",
                        timeout=30
                    )
                    assert durations_captured == [15, 15, 15, 10]


class TestDownloadImage:
    def test_download_image_writes_file(self, client, tmp_path):
        img_path = tmp_path / "test.jpg"
        mock_response = MagicMock()
        mock_response.iter_content = lambda chunk_size: [b"fake-image-data"]
        mock_response.raise_for_status = MagicMock()

        with patch("requests.get", return_value=mock_response):
            result = client.download_image(
                "https://example.com/img.jpg",
                str(img_path)
            )
            assert result == str(img_path)
            assert img_path.exists()
            assert img_path.read_bytes() == b"fake-image-data"
