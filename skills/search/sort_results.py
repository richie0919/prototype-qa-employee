from browser.seesion import get_page


SORT_OPTIONS = ["relevance", "newest", "price_asc", "price_desc"]


def sort_results(option="newest"):
    page = get_page()

    sort_dropdown = page.locator("select[name*='sort'], select[id*='sort'], [data-js-sort]").first

    sort_dropdown.wait_for(timeout=10000)
    sort_dropdown.scroll_into_view_if_needed()
    sort_dropdown.select_option(option)

    page.wait_for_load_state("networkidle")

    return f"Sorted results by: {option}"
