import os
import logging
import threading
import time
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
TOKEN = os.getenv("SECOND_BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID"))

if not TOKEN or not GROUP_CHAT_ID:
    raise RuntimeError("Missing SECOND_BOT_TOKEN or GROUP_CHAT_ID in environment variables.")

# Bot and Flask app
bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, use_context=True)

# Messages to cycle
messages = [
    "/translate Hi",
    "/translate Hello",
    "/translate How are you?",
    "/translate What’s up?",
    "/translate Nice to meet you",
    "/translate I am fine",
    "/translate Let’s go",
    "/translate Good morning",
    "/translate Good night",
    "/translate Thank you"
]

# Interval and state
interval = 600  # Default 10 minutes
msg_index = 0
lock = threading.Lock()

# Time changer command
def set_interval(update, context):
    global interval
    try:
        new_time = int(context.args[0])
        if new_time < 10:
            update.message.reply_text("⏱️ Time must be at least 10 seconds.")
            return
        with lock:
            interval = new_time
        update.message.reply_text(f"✅ Time interval set to {interval} seconds.")
    except:
        update.message.reply_text("❌ Usage: /timeset [seconds]")

# Register handler
dispatcher.add_handler(CommandHandler("timeset", set_interval))

# Message sending loop
def send_messages():
    global msg_index
    while True:
        with lock:
            msg = messages[msg_index]
            bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)
            msg_index = (msg_index + 1) % len(messages)
        time.sleep(interval)

# Start background thread
threading.Thread(target=send_messages, daemon=True).start()

# Flask routes
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

@app.route("/", methods=["GET"])
def home():
    return "✅ UptimeRobot is live!", 200

# Run app
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    logger.info("Starting UptimeRobot Flask server...")
    app.run(host="0.0.0.0", port=PORT)
