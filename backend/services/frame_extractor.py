import os
import tempfile

import cv2
import yt_dlp


# --- URL extraction ---
# Downloads a video with yt-dlp into a temp directory, then samples evenly-spaced
# frames using OpenCV. The temp directory is cleaned up automatically on exit.

def extract_frames_from_url(url: str) -> list[bytes]:
    num_frames = int(os.getenv("GEMINI_FRAMES", "5"))
    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = _download_video(url, tmpdir)
        return _sample_frames(video_path, num_frames=num_frames)


def _download_video(url: str, tmpdir: str) -> str:
    output_template = os.path.join(tmpdir, "video.%(ext)s")
    ydl_opts = {
        "format": "worst",
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    except yt_dlp.utils.DownloadError as e:
        raise ValueError(f"Could not download video: {e}")


# --- Image extraction ---
# For uploaded images, we just wrap the raw bytes in a list so both paths
# return the same type and the Gemini service doesn't need to distinguish them.

def extract_frames_from_image(file_bytes: bytes) -> list[bytes]:
    return [file_bytes]


# --- Frame sampling ---
# Samples `num_frames` frames at evenly-spaced positions across the video,
# encodes each as JPEG bytes, and skips any frames that fail to decode.

def _sample_frames(video_path: str, num_frames: int = 5) -> list[bytes]:
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frames = []
    for i in range(num_frames):
        # Offset by 0.5 so samples land in the middle of each segment
        # rather than at the very start — avoids blank/transition frames.
        frame_idx = int(((i + 0.5) / num_frames) * total)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        success, frame = cap.read()
        if not success:
            continue
        _, buffer = cv2.imencode(".jpg", frame)
        frames.append(buffer.tobytes())

    cap.release()
    return frames
