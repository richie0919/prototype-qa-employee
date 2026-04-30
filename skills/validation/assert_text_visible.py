from browser.seesion import get_page


def assert_text_visible(text):
    page = get_page()

    locator = page.locator(f"text={text}").first
    visible = locator.count() > 0

    if visible:
        return f"Text found on page: '{text}'"
    else:
        return f"Text NOT found on page: '{text}'"
