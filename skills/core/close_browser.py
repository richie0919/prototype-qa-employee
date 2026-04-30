import os


def close_browser():
    from browser.seesion import close_browser as _close

    video_path = _close()

    if video_path and os.path.exists(video_path):
        filename = os.path.basename(video_path)
        base_url = os.getenv("PUBLIC_URL", "http://localhost:8000")
        video_url = f"{base_url}/videos/{filename}"
        return f"Test finalizado. Video: {video_url}"

    return "Browser closed"
