from browser.seesion import get_page


def clear_filters():
    page = get_page()

    clear_btn = page.locator(
        "button:has-text('Clear'), button:has-text('Reset'), "
        "a:has-text('Clear all'), a:has-text('Reset filters')"
    ).first

    if clear_btn.count() == 0:
        # Uncheck all active checkboxes in the filter panel
        active = page.locator("input[type='checkbox']:checked")
        count = active.count()
        for i in range(count):
            active.nth(i).uncheck(force=True)
        page.wait_for_load_state("networkidle")
        return f"Cleared {count} active filters manually"

    clear_btn.click()
    page.wait_for_load_state("networkidle")

    return "Cleared all filters"
