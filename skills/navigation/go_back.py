from browser.seesion import get_page


def go_back():
    page = get_page()
    previous_url = page.url
    page.go_back()
    page.wait_for_load_state("domcontentloaded")
    return f"Navigated back from {previous_url} to {page.url}"
