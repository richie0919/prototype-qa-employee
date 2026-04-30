from browser.seesion import get_page
from dotenv import load_dotenv
import os

load_dotenv()

def open_site(site="prod"):
    if site == "beta":
        USERNAME = os.getenv("BETA_USERNAME")
        PASSWORD = os.getenv("BETA_PASSWORD")

        assert USERNAME and PASSWORD, "Missing BETA credentials"

        page = get_page()
        context = page.context

        context.set_http_credentials({
            "username": USERNAME,
            "password": PASSWORD
        })

        page.goto("https://hyfindrbeta.com")
        return "Opened hyfindr beta"

    else:
        page.goto("https://hyfindr.com")
        return "Opened hyfindr production"