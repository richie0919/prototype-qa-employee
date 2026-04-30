from browser.seesion import get_page

def click_product(index=0):
    page = get_page()

    all_links = page.locator(
        "a[href*='/shop/products/']:not([href*='/category/']):visible"
    )
    all_links.first.wait_for(timeout=10000)

    # Deduplicate hrefs to get one entry per product card
    seen = []
    for i in range(all_links.count()):
        href = all_links.nth(i).get_attribute("href")
        if href and href not in seen:
            seen.append(href)

    if index >= len(seen):
        return f"Only {len(seen)} products found, cannot click index {index}"

    target_href = seen[index]
    target = page.locator(f"a[href='{target_href}']:visible").first
    target.click()

    return f"Clicked product #{index + 1}"
