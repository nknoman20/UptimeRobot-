import os
import time
import threading
import logging
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
from dotenv import load_dotenv

load_dotenv()

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
TOKEN = os.getenv("SECOND_BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID", "-1001234567890"))

bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, use_context=True)

# Message list
messages = [
    "/translate Hi",
    "/translate Hello",
    "/translate How are you?",
    "/translate Good morning",
    "/translate What's up?",
    "/translate Nice to meet you",
    "/translate Welcome!",
    "/translate Let’s start",
    "/translate Thank you",
    "/translate Have a nice day"
]

index = 0
interval = 600  # Default: 10 minutes


def send_messages():
    global index
    while True:
        try:
            msg = messages[index % len(messages)]
            bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)
            logger.info(f"Sent message: {msg}")
            index += 1
        except Exception as e:
            logger.error(f"Error sending message: {e}")
        time.sleep(interval)


# /timeset command handler
def set_interval(update, context):
    global interval
    if context.args:
        try:
            new_time = int(context.args[0])
            interval = new_time
            update.message.reply_text(f"⏱ Interval set to {new_time} seconds.")
            logger.info(f"Set new interval to {new_time} seconds")
        except ValueError:
            update.message.reply_text("❌ Invalid time. Usage: /timeset 120")
    else:
        update.message.reply_text("⚠️ Usage: /timeset <seconds>")


# Command registration
dispatcher.add_handler(CommandHandler("timeset", set_interval))


@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200


@app.route("/", methods=["GET"])
def index():
    return "UptimeRobot is Live!", 200


# Start message sending thread
threading.Thread(target=send_messages, daemon=True).start()

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    logger.info("Starting UptimeRobot Flask server...")
    app.run(host="0.0.0.0", port=PORT)
