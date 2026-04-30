import os
import re
import base64
import asyncio
from flask import Flask, request, Response, send_from_directory

from dotenv import load_dotenv
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    MessageFactory,
    TurnContext,
)
from botbuilder.schema import Attachment
from botbuilder.schema import Activity

from main import run_agent_step

# -----------------------------
# 🔥 ENV
# -----------------------------
load_dotenv()

APP_ID = os.getenv("MICROSOFT_APP_ID", "")
APP_PASSWORD = os.getenv("MICROSOFT_APP_PASSWORD", "")
TENANT_ID = os.getenv("MICROSOFT_TENANT_ID", "")

# -----------------------------
# 🔥 ADAPTER
# -----------------------------
adapter_settings = BotFrameworkAdapterSettings(
    app_id=APP_ID,
    app_password=APP_PASSWORD,
    channel_auth_tenant=TENANT_ID  # optional but recommended
)

adapter = BotFrameworkAdapter(adapter_settings)

# -----------------------------
# 🔥 FLASK
# -----------------------------
app = Flask(__name__)

# simple per-user session memory
sessions = {}


# -----------------------------
# 🔥 TEAMS ENDPOINT (REAL)
# -----------------------------
@app.route("/api/messages", methods=["POST"])
def messages():
    body = request.json
    activity = Activity().deserialize(body)

    async def logic(turn_context: TurnContext):
        print("🔥 MESSAGE FROM TEAMS")

        user_id = turn_context.activity.from_property.id
        text = turn_context.activity.text or ""

        print("👤 User:", user_id)
        print("💬 Text:", text)

        history = sessions.get(user_id, [])

        # Playwright sync no puede correr en asyncio → usamos thread executor
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_agent_step, text, history)

        sessions[user_id] = result["history"]

        # 🔥 build reply
        if result["type"] == "chat":
            reply = result["response"]
        else:
            reply = result["result"]

        print("🤖 Reply:", reply)

        # Extract screenshot URLs — match both ![alt](url) and [alt](url) for /screenshots/ paths
        image_pattern = re.compile(r'!?\[([^\]]*)\]\((https?://[^)]*screenshots[^)]+)\)')
        images = image_pattern.findall(reply)
        clean_reply = image_pattern.sub('', reply).strip()

        await turn_context.send_activity(clean_reply)

        for alt, url in images:
            # Resolve to local file for reliable Teams rendering
            local_path = None
            if '/screenshots/' in url:
                filename = url.split('/screenshots/')[-1]
                local_path = os.path.join(os.path.dirname(__file__), 'screenshots', filename)

            if local_path and os.path.exists(local_path):
                with open(local_path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                content_url = f"data:image/png;base64,{image_data}"
                content_type = "image/png"
            else:
                content_url = url
                ext = url.split('.')[-1].split('?')[0].lower()
                content_type = f"image/{ext}" if ext in ('png', 'jpg', 'jpeg', 'gif', 'webp') else "image/png"

            attachment = Attachment(content_type=content_type, content_url=content_url, name=alt or "screenshot")
            await turn_context.send_activity(MessageFactory.attachment(attachment))

    # 🔥 Flask no es async → creamos loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    auth_header = request.headers.get("Authorization", "")

    loop.run_until_complete(
        adapter.process_activity(activity, auth_header, logic)
    )

    return Response(status=200)


# -----------------------------
# 🧪 CHAT NORMAL (POSTMAN)
# -----------------------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json

    message = data.get("message", "")
    session_id = data.get("session_id", "default")

    history = sessions.get(session_id, [])

    result = run_agent_step(message, history)

    sessions[session_id] = result["history"]

    return {
        "response": result["result"]
    }


# -----------------------------
# 🔥 HEALTH CHECK
# -----------------------------
@app.route("/", methods=["GET"])
def health():
    return "OK"


# -----------------------------
# 🎬 VIDEOS
# -----------------------------
VIDEOS_DIR = os.path.join(os.path.dirname(__file__), "videos")

@app.route("/videos/<path:filename>", methods=["GET"])
def serve_video(filename):
    return send_from_directory(VIDEOS_DIR, filename)


# -----------------------------
# 📸 SCREENSHOTS
# -----------------------------
SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "screenshots")

@app.route("/screenshots/<path:filename>", methods=["GET"])
def serve_screenshot(filename):
    return send_from_directory(SCREENSHOTS_DIR, filename)


# -----------------------------
# 🚀 RUN
# -----------------------------
if __name__ == "__main__":
    print("🚀 Server running on http://localhost:8000")

    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False,
        use_reloader=False  # 🔥 evita doble Playwright
    )