from browser.seesion import get_page


def check_pagination(page_number=2):
    page = get_page()

    page_btn = page.locator(
        f"a[aria-label='Page {page_number}'], "
        f"a:has-text('{page_number}'), "
        f"button:has-text('{page_number}')"
    ).first

    if page_btn.count() == 0:
        return f"No pagination found — page {page_number} not available"

    page_btn.scroll_into_view_if_needed()
    page_btn.click()
    page.wait_for_load_state("networkidle")

    return f"Navigated to page {page_number}"
