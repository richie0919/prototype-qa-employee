from browser.seesion import get_page


def get_results_count():
    page = get_page()

    products = page.locator("a[href*='/shop/products/']:not([href*='/category/'])")
    count = products.count()

    return f"Found {count} products on page"
