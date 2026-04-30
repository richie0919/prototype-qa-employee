from browser.seesion import get_page

def add_to_wishlist():
    print("❤️ Adding to wishlist")

    page = get_page()
    buttons = page.locator("[data-js-add-to-list]:visible")

    if buttons.count() == 0:
        return "No wishlist buttons found"

    buttons.first.click()
    page.wait_for_timeout(500)

    return "Added product to wishlist"