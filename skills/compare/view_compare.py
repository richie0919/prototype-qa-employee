from browser.seesion import get_page


def view_compare():
    page = get_page()

    compare_link = page.locator(
        "a[href*='/compare'], button:has-text('Compare'), a:has-text('Compare')"
    ).first

    compare_link.wait_for(timeout=10000)
    compare_link.click()

    page.wait_for_load_state("domcontentloaded")

    # Count how many products are being compared
    product_columns = page.locator("table th:not(:first-child), .compare-product, [data-compare-item]")
    count = product_columns.count()

    return f"Compare page loaded with {count} product(s)"
