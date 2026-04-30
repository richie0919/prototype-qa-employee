from browser.seesion import get_page

def click_product():

    page = get_page()
    product = page.locator(
        "a[href*='/shop/products/']:not([href*='/category/']):visible"
    ).first

    product.wait_for(timeout=10000)
    product.click()

    return "Clicked product"