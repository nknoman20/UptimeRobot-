import os
import logging
import random
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
import threading
import time

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Env Variables
TOKEN = os.getenv("SECOND_BOT_TOKEN")
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")

if not TOKEN or not GROUP_CHAT_ID:
    raise RuntimeError("SECOND_BOT_TOKEN or GROUP_CHAT_ID missing in environment!")

bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, use_context=True)

# Message list
messages = [
    "/translate Hi",
    "/translate Hello",
    "/translate How are you?",
    "/translate Good morning",
    "/translate Good night",
    "/translate What's your name?",
    "/translate Where are you from?",
    "/translate I love Bangladesh",
    "/translate Have a nice day",
    "/translate Thank you"
]

# Interval and index
interval = 600  # default 10 min
index = 0
lock = threading.Lock()

# Function to send message every X time
def send_messages():
    global index
    while True:
        with lock:
            msg = messages[index]
            bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)
            index = (index + 1) % len(messages)
        time.sleep(interval)

# Command to update interval
def set_time(update: Update, context: CallbackContext):
    global interval
    try:
        mins = int(context.args[0])
        if 1 <= mins <= 60:
            with lock:
                interval = mins * 60
            update.message.reply_text(f"✅ Interval set to {mins} minute(s).")
        else:
            update.message.reply_text("❌ Please choose between 1 and 60 minutes.")
    except:
        update.message.reply_text("❌ Usage: /timeset <minutes> (e.g., /timeset 10)")

dispatcher.add_handler(CommandHandler("timeset", set_time))

# Webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "✅ UptimeRobot is running", 200

# 🟢 Start thread when app starts
def start_thread():
    thread = threading.Thread(target=send_messages)
    thread.daemon = True
    thread.start()

if __name__ == "__main__":
    start_thread()  # ✅ Start message sending loop
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)
