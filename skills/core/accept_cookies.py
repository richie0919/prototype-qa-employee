def accept_cookies():
    from browser.seesion import get_page

    page = get_page()
    accepted = False

    locator = page.locator("text=Accept & Continue")
    if locator.count() > 0:
        locator.first.click()
        accepted = True

    if not accepted:
        for frame in page.frames:
            locator = frame.locator("text=Accept & Continue")
            if locator.count() > 0:
                locator.first.click()
                accepted = True
                break

    return "Cookies accepted" if accepted else "No banner"