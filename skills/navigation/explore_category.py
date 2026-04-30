from browser.seesion import get_page
import random

VALID_CATEGORIES = [
    "Aftercoolers",
    "Analyzers",
    "Blowers",
    "Compressors",
    "Valves",
    "Filters",
    "Hydrogen Pumps",
    "Pipes",
    "Sensors",
]

def explore_category(category=None):
    if category not in VALID_CATEGORIES:
        return f"Invalid category '{category}'. Valid options: {', '.join(VALID_CATEGORIES)}"

    print(f"🧭 Exploring: {category}")

    page = get_page()
    # abrir menú
    menu = page.locator("a[title='Components']").first
    menu.hover()

    # click categoría
    category_link = page.locator(f"a[title='{category}']").first
    category_link.wait_for(timeout=10000)
    category_link.click()

    page.wait_for_load_state("networkidle")

    return f"Explored category {category}"