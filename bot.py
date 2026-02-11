"""
PROJECT: File Sharing Bot Maker (Premium Edition)
BRANDING: Catalyst Mystery Official
VERSION: 2.0 (Deep Debugging Enabled)
"""

import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
from flask import Flask
import threading
import os
import logging

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CatalystEngine")

# --- WEB WRAPPER FOR HOSTING ---
app = Flask(__name__)
@app.route('/')
def status_page():
    return "CATALYST MYSTERY BOT MAKER IS ACTIVE 🚀", 200

# --- CONFIGURATION ---
TOKEN = "8504840971:AAFJ2L-zo1Dz8mhM31K4VZS25zKxn5ghNVw"
SESSION_ID = "112gf4b2ga004kbmqet5ns60vc"
REMOTE_URL = "https://fileshare.smms.host/user/create-bot.php"
OFFICIAL_CHANNEL = "https://t.me/CatalystMystery"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
user_states = {}

# --- DYNAMIC UI COMPONENTS ---

def get_main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🚀 DEPLOY NEW BOT", callback_data="start_deploy"),
        types.InlineKeyboardButton("🌐 OFFICIAL CHANNEL", url=OFFICIAL_CHANNEL),
        types.InlineKeyboardButton("🛠 SUPPORT", url="https://t.me/dex4dev")
    )
    return markup

def get_cancel_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ CANCEL", callback_data="cancel_action"))
    return markup

# --- CORE HANDLERS ---

@bot.message_handler(commands=['start'])
def welcome_handler(message):
    welcome_text = (
        "<b>💎 FILE SHARING BOT MAKER</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Welcome to the premium automated deployment gateway by <b>Catalyst Mystery</b>.\n\n"
        "<b>System Status:</b> Operational 🟢\n"
        "<b>Cloud:</b> Render-Nodes-01\n\n"
        "<i>Select an action to proceed:</i>"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

@bot.callback_query_handler(func=lambda call: True)
def query_router(call):
    if call.data == "start_deploy":
        bot.edit_message_text(
            "<b>STEP 1: CREDENTIALS</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Send your <b>Bot Token</b> from @BotFather:",
            call.message.chat.id, call.message.message_id, reply_markup=get_cancel_menu()
        )
        user_states[call.message.chat.id] = {'step': 'token'}
    
    elif call.data == "cancel_action":
        user_states.pop(call.message.chat.id, None)
        bot.edit_message_text("❌ <b>Process terminated by user.</b>", call.message.chat.id, call.message.message_id, reply_markup=get_main_menu())

@bot.message_handler(func=lambda message: message.chat.id in user_states)
def collection_wizard(message):
    chat_id = message.chat.id
    current_step = user_states[chat_id]['step']

    if current_step == 'token':
        user_states[chat_id]['token'] = message.text
        user_states[chat_id]['step'] = 'storage'
        bot.send_message(chat_id, "<b>STEP 2: STORAGE</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\nEnter your <b>Storage Channel ID</b>:", reply_markup=get_cancel_menu())

    elif current_step == 'storage':
        user_states[chat_id]['storage'] = message.text
        user_states[chat_id]['step'] = 'owner'
        bot.send_message(chat_id, "<b>STEP 3: FORCED SUB</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\nEnter <b>Owner Channel ID</b> (or /skip):", reply_markup=get_cancel_menu())

    elif current_step == 'owner':
        user_states[chat_id]['owner'] = "" if message.text == "/skip" else message.text
        user_states[chat_id]['step'] = 'admins'
        bot.send_message(chat_id, "<b>STEP 4: ADMIN ACCESS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\nEnter <b>Admin IDs</b> (separated by commas):", reply_markup=get_cancel_menu())

    elif current_step == 'admins':
        user_states[chat_id]['admins'] = message.text
        execute_deployment(chat_id)

def execute_deployment(chat_id):
    ctx = user_states[chat_id]
    status_node = bot.send_message(chat_id, "🔄 <b>INITIALIZING HANDSHAKE...</b>\n<i>Parsing server security layers...</i>")
    
    try:
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 12; LAVA Blaze Build/SP1A.210812.016) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.132 Mobile Safari/537.36",
            "Cookie": f"PHPSESSID={SESSION_ID}",
            "Referer": REMOTE_URL
        }
        
        # Phase 1: Authentication & Token Retrieval
        response = session.get(REMOTE_URL, headers=headers, timeout=15)
        
        if "login.php" in response.url:
            bot.edit_message_text("❌ <b>SESSION EXPIRED</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\nThe PHPSESSID is no longer valid. Update it in the source code.", chat_id, status_node.message_id, reply_markup=get_main_menu())
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': '_csrf_token'})
        
        if not csrf_token:
            bot.edit_message_text("❌ <b>SERVER SECURITY BLOCK</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\nCloud security layers blocked the connection. Try a different hosting IP.", chat_id, status_node.message_id)
            return

        # Phase 2: Deployment
        payload = {
            "_csrf_token": csrf_token['value'],
            "bot_token": ctx['token'],
            "storage_channel_id": ctx['storage'],
            "owner_channel_id": ctx['owner'],
            "admin_ids": ctx['admins']
        }
        
        final_response = session.post(REMOTE_URL, headers=headers, data=payload, timeout=20)
        final_soup = BeautifulSoup(final_response.text, 'html.parser')

        # Phase 3: Exact Response Feedback
        success_box = final_soup.find('div', {'class': 'alert-success'})
        error_box = final_soup.find('div', {'class': 'alert-error'})

        if success_box:
            clean_msg = success_box.get_text(strip=True).replace('×', '')
            bot.edit_message_text(f"✅ <b>DEPLOYMENT SUCCESS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n{clean_msg}", chat_id, status_node.message_id, reply_markup=get_main_menu())
        elif error_box:
            clean_msg = error_box.get_text(strip=True).replace('×', '')
            bot.edit_message_text(f"❌ <b>SERVER REJECTION</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n{clean_msg}", chat_id, status_node.message_id, reply_markup=get_main_menu())
        else:
            snippet = final_response.text[:100]
            bot.edit_message_text(f"⚠️ <b>UNDEFINED RESPONSE</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\nCode: {final_response.status_code}\nSnippet: <code>{snippet}...</code>", chat_id, status_node.message_id, reply_markup=get_main_menu())
            
    except Exception as e:
        bot.edit_message_text(f"☢️ <b>ENGINE CRASH</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\nError: <code>{str(e)}</code>", chat_id, status_node.message_id)
    
    user_states.pop(chat_id, None)

# --- BOOT ---
if __name__ == '__main__':
    # Start Port Exposure Thread
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()
    
    bot.set_my_commands([types.BotCommand("start", "Launch Catalyst Menu")])
    logger.info("Catalyst Mystery Service is Polling...")
    bot.infinity_polling()
