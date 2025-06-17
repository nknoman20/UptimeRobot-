import os
import logging
import threading
import time
from flask import Flask, request
import telegram
from telegram import Update
from telegram.ext import Dispatcher, CommandHandler

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
TOKEN = os.getenv("SECOND_BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_CHAT_ID"))

if not TOKEN or not GROUP_ID:
    raise RuntimeError("Missing SECOND_BOT_TOKEN or GROUP_CHAT_ID")

# Message list
messages = [
    "/translate Hi",
    "/translate Hello",
    "/translate How are you?",
    "/translate What is your name?",
    "/translate I am fine",
    "/translate Nice to meet you",
    "/translate Where are you from?",
    "/translate Good morning",
    "/translate Thank you",
    "/translate Welcome"
]

# Globals
message_index = 0
interval = 600  # Default: 10 minutes

# Initialize
app = Flask(__name__)
bot = telegram.Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

def send_messages():
    global message_index
    while True:
        try:
            msg = messages[message_index]
            bot.send_message(chat_id=GROUP_ID, text=msg)
            logger.info(f"Sent message: {msg}")
            message_index = (message_index + 1) % len(messages)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
        time.sleep(interval)

# Command: /timeset
def set_interval(update: Update, context):
    global interval
    try:
        if context.args:
            new_time = int(context.args[0])
            if new_time < 10:
                update.message.reply_text("❌ Minimum interval is 10 seconds.")
                return
            interval = new_time
            update.message.reply_text(f"✅ Time interval updated to {new_time} seconds.")
        else:
            update.message.reply_text("⚠️ Usage: /timeset <seconds>")
    except Exception as e:
        update.message.reply_text("❌ Invalid time format.")

dispatcher.add_handler(CommandHandler("timeset", set_interval))

# Webhook route
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "✅ UptimeRobot is live!", 200

if __name__ == "__main__":
    threading.Thread(target=send_messages).start()
    logger.info("Starting UptimeRobot Flask server...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
