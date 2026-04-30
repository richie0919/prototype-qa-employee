from browser.seesion import get_page

def add_to_compare():
    print("⚖️ Adding product to compare")

    page = get_page()
    buttons = page.locator("[data-js-add-to-compare]:visible")

    if buttons.count() < 2:
        return "Not enough products to compare"

    buttons.nth(0).click()
    page.wait_for_timeout(500)

    buttons.nth(1).click()
    page.wait_for_timeout(500)

    return "Added products to compare"