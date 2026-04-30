from browser.seesion import get_page


def get_product_details():
    page = get_page()

    details = {}

    # Product name
    name = page.locator("h1").first
    if name.count() > 0:
        details["name"] = name.inner_text().strip()

    # Supplier / manufacturer
    supplier = page.locator("[data-supplier], .supplier-name, a[href*='/supplier/'], a[href*='/vendor/']").first
    if supplier.count() > 0:
        details["supplier"] = supplier.inner_text().strip()

    # Quote / price availability
    if page.locator("text=Request Quote").count() > 0:
        details["pricing"] = "quote_required"
    elif page.locator("text=Add to Cart").count() > 0:
        details["pricing"] = "price_available"
    else:
        details["pricing"] = "unknown"

    # Specs table
    rows = page.locator("table tr, dl dt, .spec-label")
    spec_count = rows.count()
    if spec_count > 0:
        details["specs_found"] = spec_count

    return f"Product details: {details}"
