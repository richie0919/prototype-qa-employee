import os
from browser.seesion import get_page


def take_screenshot(name="screenshot"):
    page = get_page()

    screenshots_dir = "screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)

    safe_name = name.replace(" ", "_").replace("/", "_")
    path = os.path.join(screenshots_dir, f"{safe_name}.png")

    page.screenshot(path=path, full_page=False)

    base_url = os.getenv("PUBLIC_URL", "http://localhost:8000")
    url = f"{base_url}/screenshots/{safe_name}.png"

    return f"Screenshot saved: [{safe_name}]({url})"
