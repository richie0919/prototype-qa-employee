from browser.seesion import get_page


def click_supplier():
    page = get_page()

    supplier_link = page.locator(
        "a[href*='/supplier/'], a[href*='/vendor/'], a[href*='/company/']"
    ).first

    supplier_link.wait_for(timeout=10000)
    name = supplier_link.inner_text().strip()
    supplier_link.click()

    page.wait_for_load_state("domcontentloaded")

    return f"Navigated to supplier: {name}"
