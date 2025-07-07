# Telegram Bot

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

## 1. Import
```
import csv
import json
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
```
`csv`: Lets me read the `gospel.csv` file where the scripture verses are stored.

`json`: Reads and writes JSON (used to track which message to send next).

`os`: Checks if files like `chat_ids.txt` exist, and creates them if not.

`asyncio`: Supports running async code (Telegram bots require this).

`telegram`: Provides classes for handling updates and user interactions.

`telegram.ext`: Tools to build the bot, add handlers, and manage context.

`apscheduler`: Schedules the daily messages (runs them at 6AM UTC).

## 2. File Paths
```
CSV_FILE = "gospel.csv"
CHAT_IDS_FILE = "chat_ids.txt"
INDEX_FILE = "last_index.json"
```
Defines file names used by the bot:

`CSV_FILE`: Stores your daily messages.

`CHAT_IDS_FILE`: Keeps track of user chat IDs who subscribe via /start.

`INDEX_FILE`: Saves which message was sent last, so the bot knows where to continue.

## 3. Load Messages from CSV
```
def load_messages(csv_file):
    messages = []
    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
```
Opens `gospel.csv`, reads it as a list of dictionaries (each row is `{message: "..."}`).

```
for row in reader:
    msg = row['message'].strip()
```
Gets the message column, trims spaces.

```
print(f"Messages loaded: {messages}")
return messages
```
Print all loaded messages for debugging, then return them.

## 4. Save & Load Chat IDs

### Save New Chat IDs
```
def save_chat_id(chat_id):
    if not os.path.exists(CHAT_IDS_FILE):
        open(CHAT_IDS_FILE, "w").close()
```
If `chat_ids.txt` doesn’t exist, create an empty file.

```
with open(CHAT_IDS_FILE, "r+") as f:
  ids = {line.strip() for line in f.readlines()}
```
Read existing chat IDs into a set (to avoid duplicates).

```
if str(chat_id) not in ids:
    f.write(f"{chat_id}\n")
        print(f"Added new chat ID: {chat_id}")
```
Add the new `chat_id` if not already saved.

### Load All Chat IDs
```
def load_chat_ids():
    if not os.path.exists(CHAT_IDS_FILE):
        return []
with open(CHAT_IDS_FILE, "r") as f:
    return [line.strip() for line in f.readlines()]
```
Return an empty list if no IDs file exists. Otherwise, return all stored chat IDs as a list.

## 5. Save & Load Last Sent Message Index
### Load Index
```
def load_last_index():
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_index", 0)
    return 0
```
Reads `last_index.json`. Returns saved index or 0 if file doesn’t exist.

### Save Index
```
def save_last_index(index):
    with open(INDEX_FILE, "w") as f:
        json.dump({"last_index": index}, f)
```
Saves the current index to `last_index.json`.

### Global Varieties
```
messages = load_messages(CSV_FILE)
current_index = load_last_index()
```
Loads all messages and remembers where it left off.

## 6. Send Daily Verses
```
async def send_daily_message(context: ContextTypes.DEFAULT_TYPE):
    global current_index
    chat_ids = load_chat_ids()
```
Loads all chat IDs and keeps track of current index.

```
if not chat_ids:
  print("No chat IDs to send to.")
    return
```
If no users have subscribed, exit.

```
message = messages[current_index]
  for chat_id in chat_ids:
    try:
      await context.bot.send_message(chat_id=chat_id, text=message)
      print(f"Sent to {chat_id}: {message}")
```
Sends the current message to every chat ID.

```
except Exception as e:
    print(f"Failed to send to {chat_id}: {e}")
```
Catches errors if sending fails for a chat ID.

```
current_index = (current_index + 1) % len(messages)
save_last_index(current_index)
```
Updates the index, wrapping to 0 when reaching the end of the message list.

## 7. Handle `/start` Command

```
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    save_chat_id(chat_id)
    await update.message.reply_text("Blessed art thou, for you are now bound to the daily revelations of the Young-Girl.
    At the hour of first light, her scripture shall find you.")
```
When a user sends `/start`, saves their `chat_id` and sends a welcome message.

## 8. Main Function
```
async def main():
    app = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()
    app.add_handler(CommandHandler("start", start))
```
Creates the Telegram bot and adds a handler for `/start`.

```
scheduler = AsyncIOScheduler(timezone="UTC")
scheduler.add_job(send_daily_message, "cron", hour=6, minute=0, args=[app])
scheduler.start()
```
Schedules `send_daily_message` to run every day at 6AM UTC.

```
print("Bot is running and will send daily messages at 6AM UTC.")
await send_daily_message(app)
```
Sends a message immediately on startup as a test.

```
await app.run_polling()
```
Starts polling Telegram for incoming updates (listens for `/start`).

## 9. Run Bot
```
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        print(f"RuntimeError: {e}")
```
Runs `main()` when the script starts. Handles the “event loop already running” error.
