from browser.seesion import get_page

def adjust_slider(name="Max Rotational Speed", value=15000):
    print(f"🎚 Adjusting slider: {name}")

    page = get_page()
    section = page.get_by_text(name).first
    section.wait_for(timeout=10000)
    section.scroll_into_view_if_needed()
    section.click()

    slider = page.locator("input[type='range']")
    if slider.count() > 0:
        slider.first.fill(str(value))

    page.wait_for_load_state("networkidle")

    return f"Adjusted slider {name} to {value}"