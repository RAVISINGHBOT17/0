#!/usr/bin/python3
import telebot
import datetime
import random
import string
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

# ATTACK CONTROL BUTTONS
def attack_control_buttons(user_id):
    keyboard = types.InlineKeyboardMarkup()
    if user_attack_status.get(user_id, False):
        keyboard.add(types.InlineKeyboardButton("❌ Turn OFF Attack", callback_data=f"toggle_attack_{user_id}_off"))
    else:
        keyboard.add(types.InlineKeyboardButton("✅ Turn ON Attack", callback_data=f"toggle_attack_{user_id}_on"))
    return keyboard

# ATTACK BUTTON SHOW KARNE WALA FUNCTION
@bot.message_handler(commands=['attack'])
def send_attack_control(message):
    user_id = message.from_user.id

    if user_id not in user_keys:
        bot.reply_to(message, "❌ PEHLE /redeem KARKAY ACCESS LO!")
        return

    if datetime.datetime.now() > user_keys[user_id]:
        bot.reply_to(message, "⏳ TERA ACCESS EXPIRE HO CHUKA HAI! ADMIN SE BAAT KAR.")
        return

    bot.send_message(message.chat.id, "⚡ Apna attack control karo:", reply_markup=attack_control_buttons(user_id))

# CALLBACK HANDLER FOR BUTTON CLICKS
@bot.callback_query_handler(func=lambda call: call.data.startswith("toggle_attack_"))
def toggle_attack(call):
    user_id = int(call.data.split("_")[2])
    action = call.data.split("_")[3]

    if user_id != call.from_user.id:
        bot.answer_callback_query(call.id, "🚫 YE BUTTON SIRF APKE LIYE HAI!")
        return

    if action == "on":
        user_attack_status[user_id] = True
        bot.edit_message_text("✅ Attack ON!", call.message.chat.id, call.message.message_id, reply_markup=attack_control_buttons(user_id))
    else:
        user_attack_status[user_id] = False
        bot.edit_message_text("❌ Attack OFF!", call.message.chat.id, call.message.message_id, reply_markup=attack_control_buttons(user_id))

# START POLLING
bot.polling(none_stop=True)