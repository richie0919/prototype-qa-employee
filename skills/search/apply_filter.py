from browser.seesion import get_page

def apply_filter(filter_name="Compressor Type"):
    print(f"🎛 Applying filter: {filter_name}")

    page = get_page()
    filter_section = page.get_by_text(filter_name).first
    filter_section.wait_for(timeout=10000)
    filter_section.scroll_into_view_if_needed()
    filter_section.click()

    # seleccionar primer checkbox disponible
    options = page.locator("input[type='checkbox']")
    if options.count() > 0:
        options.first.check(force=True)

    page.wait_for_load_state("networkidle")

    return f"Applied filter: {filter_name}"