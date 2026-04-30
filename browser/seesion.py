import os
from playwright.sync_api import sync_playwright

_playwright = None
_browser = None
_context = None
_page = None

VIDEOS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "videos"))


def _new_context(http_credentials=None):
    global _context, _page

    # Cierra contexto anterior guardando el video
    if _context:
        _context.close()
        _context = None
        _page = None

    os.makedirs(VIDEOS_DIR, exist_ok=True)

    kwargs = {
        "record_video_dir": VIDEOS_DIR,
        "record_video_size": {"width": 1280, "height": 720},
    }
    if http_credentials:
        kwargs["http_credentials"] = http_credentials

    _context = _browser.new_context(**kwargs)
    _page = _context.new_page()
    return _page


def get_page(http_credentials=None):
    global _playwright, _browser, _context, _page

    if _playwright is None:
        os.makedirs(VIDEOS_DIR, exist_ok=True)
        _playwright = sync_playwright().start()
        _browser = _playwright.chromium.launch(headless=False)

    if _page is None:
        _new_context(http_credentials)

    return _page


def get_page_with_credentials(username, password):
    """Recrea el contexto con HTTP Basic Auth (para beta)."""
    global _page
    _page = _new_context(http_credentials={"username": username, "password": password})
    return _page


def close_browser():
    global _playwright, _browser, _context, _page

    video_path = None

    if _page:
        try:
            video_path = _page.video.path()
        except Exception:
            pass

    if _context:
        _context.close()  # context.close() finaliza y guarda el video
        _context = None
        _page = None

    if _browser:
        _browser.close()
        _browser = None

    if _playwright:
        _playwright.stop()
        _playwright = None

    return video_path