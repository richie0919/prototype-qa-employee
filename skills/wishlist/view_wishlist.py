from browser.seesion import get_page


def view_wishlist():
    page = get_page()

    wishlist_link = page.locator(
        "a[href*='/wishlist'], a[href*='/saved'], a[href*='/list'], "
        "a:has-text('Wishlist'), a:has-text('Saved items')"
    ).first

    wishlist_link.wait_for(timeout=10000)
    wishlist_link.click()

    page.wait_for_load_state("domcontentloaded")

    items = page.locator("a[href*='/shop/products/']:not([href*='/category/'])")
    count = items.count()

    return f"Wishlist page loaded with {count} saved product(s)"
