import yt_dlp
import cv2
import os

def test_extract(url: str):

    # Configure yt-dlp — lowest quality for speed, save as test_video.mp4/webm/etc
    ydl_opts = {
        'format': 'worst',
        'outtmpl': 'test_video.%(ext)s',
        'quiet': False,
    }

    # Download the video and get the path it was saved to
    print(f"Downloading: {url}")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        path = ydl.prepare_filename(info)
    print(f"Downloaded to: {path}")

    # Open the video with OpenCV and get the total frame count
    cap = cv2.VideoCapture(path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Total frames in video: {total}")

    # Sample 3 frames evenly spaced across the video and save each as a JPEG
    for i in range(3):
        idx = int((i / 3) * total)
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            filename = f"frame_{i}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Saved {filename}")
        else:
            print(f"Could not read frame {i}")

    # Release the video file and delete the downloaded video — only the frames are needed
    cap.release()
    os.remove(path)
    print("Done — video file cleaned up")

# Paste a real public TikTok URL here to test
test_extract("https://www.tiktok.com/@justinhansome/video/7620624252529626398?is_from_webapp=1&sender_device=pc")