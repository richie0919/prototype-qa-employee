from browser.seesion import get_page

def validate_page():
    page = get_page()
    title = page.title()
    return f"Page title: {title}"