from browser.seesion import get_page
import random

VALID_QUERIES = [
    "air compressor",
    "hydrogen valve",
    "industrial filter",
    "pressure regulator",
    "gas compressor"
]

def search(query=None):
    if not query:
        query = random.choice(VALID_QUERIES)

    print(f"🔎 Searching: {query}", flush=True)

    page = get_page()

    if page.url in ("about:blank", ""):
        raise RuntimeError("Page is blank — call open_home first (site='prod' or site='beta')")

    search_input = page.get_by_role("textbox", name="Chat with me to find products")

    search_input.click()
    search_input.fill(query)

    try:
        search_input.press("Enter")
    except:
        page.get_by_role("button").last.click()

    page.wait_for_url("**/ai-search**", timeout=20000)
    page.wait_for_load_state("networkidle")

    return f"Searched {query}"