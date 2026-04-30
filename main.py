import json
import inspect
from llm import ask_llm

from utils.memory import load_memory, add_entry

# Skills
from skills.core.open_home import open_home
from skills.core.accept_cookies import accept_cookies
from skills.core.close_browser import close_browser
from skills.search.search import search
from skills.product.click_product import click_product
from skills.validation.validate_page import validate_page
from skills.navigation.explore_category import explore_category
from skills.search.apply_filter import apply_filter
from skills.search.adjust_slider import adjust_slider
from skills.compare.add_to_compare import add_to_compare
from skills.compare.view_compare import view_compare
from skills.wishlist.add_to_wishlist import add_to_wishlist
from skills.wishlist.view_wishlist import view_wishlist
from skills.product.get_product_details import get_product_details
from skills.product.click_supplier import click_supplier
from skills.search.get_results_count import get_results_count
from skills.search.sort_results import sort_results
from skills.search.clear_filters import clear_filters
from skills.navigation.go_back import go_back
from skills.navigation.check_pagination import check_pagination
from skills.validation.assert_text_visible import assert_text_visible
from skills.validation.take_screenshot import take_screenshot


def open_site(url=None, site="prod"):
    """Flexible alias: accepts a direct URL or delegates to open_home with site=prod/beta."""
    if url:
        from browser.seesion import get_page
        page = get_page()
        page.goto(url)
        return f"Opened {url}"
    return open_home(site=site)


SKILLS = {
    "open_home": open_home,
    "open_site": open_site,
    "accept_cookies": accept_cookies,
    "search": search,
    "click_product": click_product,
    "validate_page": validate_page,
    "explore_category": explore_category,
    "apply_filter": apply_filter,
    "adjust_slider": adjust_slider,
    "add_to_compare": add_to_compare,
    "view_compare": view_compare,
    "add_to_wishlist": add_to_wishlist,
    "view_wishlist": view_wishlist,
    "get_product_details": get_product_details,
    "click_supplier": click_supplier,
    "get_results_count": get_results_count,
    "sort_results": sort_results,
    "clear_filters": clear_filters,
    "go_back": go_back,
    "check_pagination": check_pagination,
    "assert_text_visible": assert_text_visible,
    "take_screenshot": take_screenshot,
    "close_browser": close_browser,
}


# -----------------------------
# Prompt
# -----------------------------
def load_prompt():
    with open("prompts/qa_agent.md", "r") as f:
        return f.read()


# -----------------------------
# Extract all JSON blocks safely
# -----------------------------
def extract_all_json(text):
    """Finds all top-level JSON objects in the text."""
    results = []
    depth = 0
    start = None
    for i, ch in enumerate(text):
        if ch == '{':
            if depth == 0:
                start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start is not None:
                try:
                    results.append(json.loads(text[start:i+1]))
                except json.JSONDecodeError:
                    pass
                start = None
    if not results:
        raise ValueError("No JSON found")
    return results


# -----------------------------
# 🔥 SINGLE STEP (for API / Teams)
# -----------------------------
def run_agent_step(user_input, history=None):
    # Abre el navegador localmente al recibir el mensaje
    from browser.seesion import get_page
    get_page()

    system_prompt = load_prompt()

    if history is None:
        history = []

    persistent_memory = load_memory()

    # memory context
    memory_text = "\n".join(
        [f"{h['skill']} -> {h['result']}" for h in history[-5:]]
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "system",
            "content": f"""
Previous actions:
{memory_text}

Avoid repeating actions.
"""
        },
        {"role": "user", "content": user_input}
    ]

    try:
        response = ask_llm(messages)
        print("🧠 RAW:", response, flush=True)

        # ----------------------------------
        # 🔥 DETECT JSON IN LLM RESPONSE
        # ----------------------------------
        try:
            actions = extract_all_json(response)
            print(f"🎯 Found {len(actions)} action(s)", flush=True)
        except Exception:
            actions = None

        if actions:
            # Remove consecutive duplicate skill calls (same skill + same args back to back)
            deduped = []
            for action in actions:
                if deduped and deduped[-1].get("skill") == action.get("skill") and deduped[-1].get("args") == action.get("args"):
                    print(f"⏭️ Skipping duplicate skill call: {action.get('skill')}", flush=True)
                    continue
                deduped.append(action)
            actions = deduped

            last_result = None
            skill_names = []
            for action in actions:
                skill = action.get("skill")
                args = action.get("args", {})
                skill_names.append(skill)

                print(f"👉 {skill} | {args}", flush=True)

                try:
                    if skill in SKILLS:
                        fn = SKILLS[skill]
                        valid_params = inspect.signature(fn).parameters
                        filtered_args = {k: v for k, v in args.items() if k in valid_params}
                        last_result = fn(**filtered_args)
                    else:
                        last_result = f"Unknown skill: {skill}"

                    print(f"✅ {skill} result: {last_result}", flush=True)

                    entry = {
                        "skill": skill,
                        "args": args,
                        "result": last_result
                    }
                    history.append(entry)
                    add_entry(persistent_memory, entry)

                except Exception as skill_err:
                    last_result = f"Skill '{skill}' failed: {skill_err}"
                    print(f"⚠️ {last_result}", flush=True)
                    history.append({"skill": skill, "args": args, "result": last_result})

            # Auto-close: if close_browser was not called, close and attach video
            if "close_browser" not in skill_names:
                video_result = close_browser()
                print(f"🎬 Auto-close: {video_result}", flush=True)
            else:
                video_result = last_result  # close_browser was called, its result is already in last_result

            # Programmatically extract screenshot and video URLs — never trust the LLM to pick the right one
            import re as _re

            screenshot_url = None
            video_url = None

            # Scan all history entries for a screenshot URL
            for entry in history:
                m = _re.search(r'https?://\S+/screenshots/\S+\.png', str(entry.get("result", "")))
                if m:
                    screenshot_url = m.group(0).rstrip(')')

            # Extract video URL from video_result
            if video_result:
                m = _re.search(r'https?://\S+/videos/\S+\.webm', str(video_result))
                if m:
                    video_url = m.group(0).rstrip(')')

            # Build explicit attachment lines so the LLM has nothing to invent
            media_block = ""
            if screenshot_url:
                media_block += f"\n![Screenshot]({screenshot_url})"
            if video_url:
                media_block += f"\n[Test recording]({video_url})"

            summary_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
                {
                    "role": "system",
                    "content": (
                        f"Skills executed: {', '.join(str(s) for s in skill_names)}\n"
                        f"Page visited: {next((e.get('result','') for e in history if e.get('skill') == 'validate_page'), 'unknown')}\n\n"
                        "Write a brief, friendly summary to the user in the SAME language they used above. "
                        "Do NOT include any URLs, file names, markdown links, or markdown images — those will be appended automatically after your text. "
                        "Keep it short and natural. Do NOT output JSON."
                    )
                }
            ]
            summary_text = ask_llm(summary_messages)
            last_result = summary_text.strip() + media_block
            print(f"📝 Formatted result: {last_result}", flush=True)

            return {
                "type": "action",
                "response": response,
                "result": last_result,
                "history": history
            }

        # ----------------------------------
        # 💬 CHAT NORMAL (DEFAULT)
        # ----------------------------------
        return {
            "type": "chat",
            "response": response,
            "result": response,
            "history": history
        }

    except Exception as e:
        return {
            "type": "error",
            "response": str(e),
            "result": str(e),
            "history": history
        }


# -----------------------------
# 🔥 LOOP LOCAL (opcional CLI)
# -----------------------------
def run_agent():
    history = []

    print("\n🧠 QA Agent (type 'exit' to quit)\n")

    while True:
        user_input = input("👤 You: ")

        if user_input.lower() == "exit":
            break

        result = run_agent_step(user_input, history)

        history = result["history"]

        print("🤖 Bot:", result["result"])


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    run_agent()