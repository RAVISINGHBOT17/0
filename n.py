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

def generate_key():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "🚀 *WELCOME TO THE ULTIMATE ATTACK BOT!* 🚀\n\n"
        "🔥 *POWERED BY:* 彡[RAVI]彡\n"
        "💀 *OWNER:* @R_SDanger\n"
        "⚡ *FASTEST DDOS ATTACKS AVAILABLE!*\n\n"
        "🔹 *COMMANDS:*\n"
        "`/attack <IP> <PORT> <TIME>` - *Launch an attack!*\n"
        "`/buy` - *View pricing & buy access!*\n"
        "`/redeem <key>` - *Activate access!*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def buy(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "💰 *PRICING DETAILS* 💰\n\n"
        "🔹 *1 DAY ACCESS* - ₹80\n"
        "🔹 *7 DAYS ACCESS* - ₹400\n"
        "🔹 *30 DAYS ACCESS* - ₹1200\n\n"
        "⚡ *PAYMENT METHODS:*\n"
        "✅ UPI: `ddosseller9953@axl`\n"
        "✅ PAYTM: `ddosseller9953@axl`\n\n"
        "📩 *TO BUY, CONTACT:* @R_SDanger"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("buy", buy))
    application.run_polling()

if __name__ == '__main__':
    main()