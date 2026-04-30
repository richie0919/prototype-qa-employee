import os
import asyncio
from flask import Flask, request, Response, send_from_directory

from dotenv import load_dotenv
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    TurnContext,
)
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
    channel_auth_tenant=TENANT_ID  # opcional pero recomendado
)

adapter = BotFrameworkAdapter(adapter_settings)

# -----------------------------
# 🔥 FLASK
# -----------------------------
app = Flask(__name__)

# memoria simple por usuario
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

        # 🔥 respuesta inteligente
        if result["type"] == "chat":
            reply = result["response"]
        else:
            reply = result["result"]

        print("🤖 Reply:", reply)

        await turn_context.send_activity(reply)

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
# 🚀 RUN
# -----------------------------
if __name__ == "__main__":
    print("🚀 Server running on http://localhost:8000")
    print("🔐 APP_ID:", APP_ID if APP_ID else "EMPTY (dev mode)")
    print("🏢 TENANT:", TENANT_ID if TENANT_ID else "EMPTY")

    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False,
        use_reloader=False  # 🔥 evita doble Playwright
    )