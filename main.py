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
from skills.wishlist.add_to_wishlist import add_to_wishlist


def open_site(url=None, site="prod"):
    """Alias flexible: acepta url directa o delega a open_home con site=prod/beta."""
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
    "add_to_wishlist": add_to_wishlist,
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

    # contexto memoria
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
        # 🔥 DETECTAR JSON EN RESPUESTA DEL LLM
        # ----------------------------------
        try:
            actions = extract_all_json(response)
            print(f"🎯 Found {len(actions)} action(s)", flush=True)

            last_result = None
            for action in actions:
                skill = action.get("skill")
                args = action.get("args", {})

                print(f"👉 {skill} | {args}", flush=True)

                if skill in SKILLS:
                    fn = SKILLS[skill]
                    # Filtrar solo los args que la función acepta
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

            # 🔥 Auto-cierre: si no se llamó close_browser, cerramos y devolvemos el video
            skill_names = [a.get("skill") for a in actions]
            if "close_browser" not in skill_names:
                video_result = close_browser()
                print(f"🎬 Auto-close: {video_result}", flush=True)
                if video_result and "http" in str(video_result):
                    last_result = f"{last_result}\n\n🎬 {video_result}"

            return {
                "type": "action",
                "response": response,
                "result": last_result,
                "history": history
            }

        except Exception as e:
            import traceback
            print(f"⚠️ JSON parse error: {e}", flush=True)
            print(traceback.format_exc(), flush=True)

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