import os
import logging
import threading
import time
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler

# --- Config ---
TOKEN = os.getenv("SECOND_BOT_TOKEN")
CHAT_ID = os.getenv("GROUP_CHAT_ID")
if not TOKEN or not CHAT_ID:
    raise RuntimeError("TOKEN or CHAT_ID missing!")

# --- App & Bot Setup ---
app = Flask(__name__)
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Message & Timing ---
messages = [
    "/translate Hi",
    "/translate Hello",
    "/translate How are you?",
    "/translate Good morning",
    "/translate Good night",
    "/translate Thank you",
    "/translate I love you",
    "/translate What's your name?",
    "/translate Where are you from?",
    "/translate Nice to meet you"
]

current_index = 0
interval_seconds = 600  # Default: 10 minutes

# --- Sending Messages ---
def send_messages():
    global current_index
    while True:
        try:
            msg = messages[current_index]
            bot.send_message(chat_id=CHAT_ID, text=msg)
            logger.info(f"Sent message: {msg}")
            current_index = (current_index + 1) % len(messages)
        except Exception as e:
            logger.error(f"Send error: {e}")
        time.sleep(interval_seconds)

# --- /timeset Command Handler ---
def timeset(update, context):
    global interval_seconds
    try:
        value = int(context.args[0])
        if value < 30:
            update.message.reply_text("⚠️ Time must be at least 30 seconds.")
            return
        interval_seconds = value
        update.message.reply_text(f"✅ Interval set to {value} seconds.")
        logger.info(f"Interval changed to {value} seconds")
    except (IndexError, ValueError):
        update.message.reply_text("❌ Usage: /timeset <seconds>")

dispatcher.add_handler(CommandHandler("timeset", timeset))

# --- Telegram Webhook (Optional, not needed unless you want to handle Telegram updates)
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

@app.route("/", methods=["GET"])
def home():
    return "✅ UptimeRobot is running", 200

# --- Start Thread on Launch ---
if __name__ == "__main__":
    logger.info("Starting UptimeRobot Flask server...")

    # Start messaging thread
    thread = threading.Thread(target=send_messages)
    thread.daemon = True
    thread.start()

    # Start server
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
