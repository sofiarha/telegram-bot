import csv
import json
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler


CSV_FILE = "gospel.csv"
CHAT_IDS_FILE = "chat_ids.txt"
INDEX_FILE = "last_index.json"


def load_messages(csv_file):
    messages = []
    with open(csv_file, newline="", encoding="edt-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            msg = row['message'].strip()
    print(f"Messages loaded: {messages}")
    return messages

def save_chat_id(chat_id):
    if not os.path.exists(CHAT_IDS_FILE):
        open(CHAT_IDS_FILE, "w").close()
    with open(CHAT_IDS_FILE, "r+") as f:
        ids = {line.strip() for line in f.readlines()}
        if str(chat_id) not in ids:
            f.write(f"{chat_id}\n")
            print(f"Added new chat ID: {chat_id}")

def load_chat_ids():
    if not os.path.exists(CHAT_IDS_FILE):
        return []
    with open(CHAT_IDS_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]

def load_last_index():
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_index", 0)
    return 0

def save_last_index(index):
    with open(INDEX_FILE, "w") as f:
        json.dump({"last_index": index}, f)

messages = load_messages(CSV_FILE)
current_index = load_last_index()

async def send_daily_message(context: ContextTypes.DEFAULT_TYPE):
    global current_index
    chat_ids = load_chat_ids()
    if not chat_ids:
        print("No chat IDs to send to.")
        return
    message = messages[current_index]
    for chat_id in chat_ids:
        try:
            await context.bot.send_message(chat_id=chat_id, text=message)
            print(f"Sent to {chat_id}: {message}")
        except Exception as e:
            print(f"Failed to send to {chat_id}: {e}")
async def handle_all_updates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Received update: {update}")


    current_index = (current_index + 1) % len(messages)
    save_last_index(current_index)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Received /start from chat_id: {update.effective_chat.id}")
    chat_id = update.effective_chat.id
    save_chat_id(chat_id)
    await update.message.reply_text("Blessed art thou, for you are now bound to the daily revelations of the Young-Girl. At the hour of first light, her scripture shall find you.")

async def main():
    app = ApplicationBuilder().token("8091306656:AAHY9OmXCdBYMRNQmLLGK4VI2wFlJCuEY0A").build()
    app.add_handler(CommandHandler("start", start))

    scheduler = AsyncIOScheduler(timezone="EDT")
    scheduler.add_job(lambda: send_daily_message(app.bot), "cron", hour=6, minute=0)
    scheduler.start()

    print("Bot is running and will send daily revelations at 6AM EDT.")

    await send_daily_message(app)

    await app.run_polling()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        print(f"RuntimeError: {e}")