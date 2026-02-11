"""
PROJECT: File Sharing Bot Maker (Premium Edition)
BRANDING: Catalyst Mystery Official
HOSTING: Optimized for Render/Vercel
"""

import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
from flask import Flask
import threading
import os

# --- WEB ENGINE ---
app = Flask(__name__)
@app.route('/')
def status(): return "CATALYST MYSTERY ENGINE ONLINE", 200

# --- CORE CONFIGURATION ---
TOKEN = "8504840971:AAFJ2L-zo1Dz8mhM31K4VZS25zKxn5ghNVw"
SESSION_ID = "112gf4b2ga004kbmqet5ns60vc"
BACKEND_URL = "https://fileshare.smms.host/user/create-bot.php"
OFFICIAL_CHANNEL = "https://t.me/CatalystMystery"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
user_states = {}

# --- PREMIUM UI COMPONENTS ---

def main_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_deploy = types.InlineKeyboardButton("🚀 DEPLOY NEW BOT", callback_data="start_deploy")
    btn_channel = types.InlineKeyboardButton("🌐 OFFICIAL CHANNEL", url=OFFICIAL_CHANNEL)
    btn_support = types.InlineKeyboardButton("🛠 TECHNICAL SUPPORT", url="https://t.me/dex4dev") # Updated support
    markup.add(btn_deploy, btn_channel, btn_support)
    return markup

def back_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ CANCEL", callback_data="cancel"))
    return markup

# --- BOT LOGIC ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        f"<b>💎 FILE SHARING BOT MAKER</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Welcome to the premium automated deployment gateway by <b>Catalyst Mystery</b>.\n\n"
        f"<b>Available Modules:</b>\n"
        f"• High-Speed Deployment\n"
        f"• Auto-CSRF Handshake\n"
        f"• Cloud-Based Hosting\n\n"
        f"<i>Select an option below to proceed:</i>"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu_markup())

@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    if call.data == "start_deploy":
        bot.edit_message_text(
            "<b>STEP 1: AUTHENTICATION</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Please provide your <b>Telegram Bot Token</b> from @BotFather:",
            call.message.chat.id, call.message.message_id, reply_markup=back_markup()
        )
        user_states[call.message.chat.id] = {'step': 'token'}
    
    elif call.data == "cancel":
        user_states.pop(call.message.chat.id, None)
        bot.edit_message_text("❌ <b>Process Aborted.</b>", call.message.chat.id, call.message.message_id, reply_markup=main_menu_markup())

@bot.message_handler(func=lambda message: message.chat.id in user_states)
def deployment_step_handler(message):
    cid = message.chat.id
    state = user_states[cid]['step']

    if state == 'token':
        user_states[cid]['token'] = message.text
        user_states[cid]['step'] = 'storage'
        bot.send_message(cid, "<b>STEP 2: STORAGE</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\nEnter your <b>Storage Channel ID</b>:", reply_markup=back_markup())

    elif state == 'storage':
        user_states[cid]['storage'] = message.text
        user_states[cid]['step'] = 'owner'
        bot.send_message(cid, "<b>STEP 3: FORCED SUB</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\nEnter <b>Owner Channel ID</b> (or /skip):", reply_markup=back_markup())

    elif state == 'owner':
        user_states[cid]['owner'] = "" if message.text == "/skip" else message.text
        user_states[cid]['step'] = 'admins'
        bot.send_message(cid, "<b>STEP 4: ADMINS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\nEnter <b>Admin IDs</b> (comma separated):", reply_markup=back_markup())

    elif state == 'admins':
        user_states[cid]['admins'] = message.text
        final_submission(cid)

def final_submission(chat_id):
    data = user_states[chat_id]
    status = bot.send_message(chat_id, "🔄 <b>INITIALIZING...</b>\n<i>Establishing secure connection to Catalyst Servers...</i>")
    
    try:
        session = requests.Session()
        headers = {"User-Agent": "Mozilla/5.0", "Cookie": f"PHPSESSID={SESSION_ID}"}
        
        # CSRF Logic
        res = session.get(BACKEND_URL, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        csrf = soup.find('input', {'name': '_csrf_token'})['value']
        
        payload = {
            "_csrf_token": csrf,
            "bot_token": data['token'],
            "storage_channel_id": data['storage'],
            "owner_channel_id": data['owner'],
            "admin_ids": data['admins']
        }
        
        response = session.post(BACKEND_URL, headers=headers, data=payload)
        
        if "created successfully" in response.text:
            bot.edit_message_text(
                "✅ <b>DEPLOYMENT SUCCESSFUL</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "Your bot is now operational. Thank you for choosing Catalyst Mystery.", 
                chat_id, status.message_id, reply_markup=main_menu_markup()
            )
        else:
            bot.edit_message_text("❌ <b>DEPLOYMENT FAILED</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\nPossible session timeout or invalid token.", chat_id, status.message_id, reply_markup=main_menu_markup())
            
    except Exception as e:
        bot.edit_message_text(f"⚠️ <b>CRITICAL ERROR:</b>\n{str(e)}", chat_id, status.message_id)
    
    user_states.pop(chat_id, None)

# --- RUNTIME ---
if __name__ == '__main__':
    # Threading to keep the web port active
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()
    bot.set_my_commands([types.BotCommand("start", "Main Menu")])
    bot.infinity_polling()
