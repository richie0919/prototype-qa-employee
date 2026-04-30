def open_home(site="prod"):
    from browser.seesion import get_page, get_page_with_credentials
    from skills.core.accept_cookies import accept_cookies
    import os
    from dotenv import load_dotenv

    load_dotenv()

    if site == "beta":
        USERNAME = os.getenv("BETA_USERNAME")
        PASSWORD = os.getenv("BETA_PASSWORD")

        page = get_page_with_credentials(USERNAME, PASSWORD)
        page.goto("https://hyfindrbeta.com")
        page.wait_for_load_state("domcontentloaded")
        accept_cookies()
        return "Opened beta site"

    else:
        page = get_page()
        page.goto("https://hyfindr.com")
        page.wait_for_load_state("domcontentloaded")
        accept_cookies()
        return "Opened production site"