"""
PROJECT: File Sharing Bot Maker
BRANDING: Catalyst Mystery
ENGINE: Auto-Login Integration (zihad98)
HOSTING: Optimized for Render (Port 10000)
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
logger = logging.getLogger("CatalystMystery")

# --- WEB WRAPPER ---
app = Flask(__name__)
@app.route('/')
def health(): return "SYSTEM_ONLINE", 200

def run_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- CONFIGURATION ---
BOT_TOKEN = "8504840971:AAGcd7UkuSTy78YH4AbFMfXdz6q4RzfGPw8"
PANEL_USER = "zihad98"
PANEL_PASS = "chiragrathi123"

LOGIN_URL = "https://fileshare.smms.host/user/login.php"
CREATE_URL = "https://fileshare.smms.host/user/create-bot.php"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
user_data = {}

# --- CORE ENGINE: AUTHENTICATION ---
def get_authenticated_session():
    """Generates a fresh authenticated session for every deployment."""
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 12; LAVA Blaze Build/SP1A.210812.016)",
        "Referer": LOGIN_URL
    }
    try:
        # Step 1: Secure Login CSRF
        res = session.get(LOGIN_URL, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        csrf = soup.find('input', {'name': '_csrf_token'})
        
        payload = {"username": PANEL_USER, "password": PANEL_PASS}
        if csrf: payload["_csrf_token"] = csrf['value']

        # Step 2: Login Execution
        login_res = session.post(LOGIN_URL, data=payload, headers=headers)
        if "dashboard.php" in login_res.url or "user/index.php" in login_res.url:
            return session
        return None
    except Exception as e:
        logger.error(f"Auth Error: {e}")
        return None

# --- UI COMPONENTS ---
def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🚀 DEPLOY NEW BOT", callback_data="deploy"),
        types.InlineKeyboardButton("🌐 OFFICIAL CHANNEL", url="https://t.me/CatalystMystery"),
        types.InlineKeyboardButton("🛠 TECHNICAL SUPPORT", url="https://t.me/dex4dev")
    )
    return markup

def cancel_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ CANCEL", callback_data="home"))
    return markup

# --- HANDLERS ---
@bot.message_handler(commands=['start'])
def start(message):
    welcome = (
        "<b>💎 FILE SHARING BOT MAKER</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Welcome to the premium automated gateway by <b>Catalyst Mystery</b>.\n\n"
        "<b>Status:</b> Active 🟢\n"
        "<b>Engine:</b> Auto-Auth v2.0\n\n"
        "<i>Ready to deploy your professional bot?</i>"
    )
    bot.send_message(message.chat.id, welcome, reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    if call.data == "deploy":
        bot.edit_message_text(
            "<b>STEP 1: IDENTIFICATION</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Send your <b>Bot Token</b> from @BotFather:",
            call.message.chat.id, call.message.message_id, reply_markup=cancel_markup()
        )
        bot.register_next_step_handler(call.message, collect_token)
    elif call.data == "home":
        bot.edit_message_text("❌ <b>Operation Cancelled.</b>", call.message.chat.id, call.message.message_id, reply_markup=main_menu())

def collect_token(message):
    if not message.text or "/" in message.text: return
    user_data[message.chat.id] = {'token': message.text}
    bot.send_message(message.chat.id, "<b>STEP 2: STORAGE</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\nEnter your <b>Storage Channel ID</b>:", reply_markup=cancel_markup())
    bot.register_next_step_handler(message, collect_storage)

def collect_storage(message):
    user_data[message.chat.id]['storage'] = message.text
    bot.send_message(message.chat.id, "<b>STEP 3: FORCED SUB</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\nEnter <b>Owner Channel ID</b> (or /skip):", reply_markup=cancel_markup())
    bot.register_next_step_handler(message, collect_owner)

def collect_owner(message):
    user_data[message.chat.id]['owner'] = "" if message.text == "/skip" else message.text
    bot.send_message(message.chat.id, "<b>STEP 4: ACCESS CONTROL</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\nEnter <b>Admin IDs</b> (comma separated):", reply_markup=cancel_markup())
    bot.register_next_step_handler(message, final_deploy)

def final_deploy(message):
    cid = message.chat.id
    user_data[cid]['admins'] = message.text
    status = bot.send_message(cid, "🔄 <b>INITIALIZING...</b>\n<i>Authenticating with Catalyst Cluster...</i>")
    
    try:
        session = get_authenticated_session()
        if not session:
            bot.edit_message_text("❌ <b>AUTH FAILED</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\nEngine could not login to the panel.", cid, status.message_id, reply_markup=main_menu())
            return

        bot.edit_message_text("🔄 <b>DEPLOYING...</b>\n<i>Injecting bot parameters...</i>", cid, status.message_id)
        
        # Deployment Page CSRF
        res = session.get(CREATE_URL)
        soup = BeautifulSoup(res.text, 'html.parser')
        csrf = soup.find('input', {'name': '_csrf_token'})
        
        if not csrf:
            bot.edit_message_text("❌ <b>CSRF ERROR</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\nSecurity token retrieval failed.", cid, status.message_id, reply_markup=main_menu())
            return

        payload = {
            "_csrf_token": csrf['value'],
            "bot_token": user_data[cid]['token'],
            "storage_channel_id": user_data[cid]['storage'],
            "owner_channel_id": user_data[cid]['owner'],
            "admin_ids": user_data[cid]['admins']
        }
        
        final_res = session.post(CREATE_URL, data=payload)
        final_soup = BeautifulSoup(final_res.text, 'html.parser')

        # Result Extraction
        success = final_soup.find('div', {'class': 'alert-success'})
        error = final_soup.find('div', {'class': 'alert-error'})

        if success:
            msg = success.get_text(strip=True).replace('×', '')
            bot.edit_message_text(f"✅ <b>SUCCESS</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n{msg}", cid, status.message_id, reply_markup=main_menu())
        elif error:
            msg = error.get_text(strip=True).replace('×', '')
            bot.edit_message_text(f"❌ <b>REJECTED</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\n{msg}", cid, status.message_id, reply_markup=main_menu())
        else:
            bot.edit_message_text("⚠️ <b>UNKNOWN STATE</b>\n━━━━━━━━━━━━━━━━━━━━━━━━\nCheck dashboard for status.", cid, status.message_id, reply_markup=main_menu())

    except Exception as e:
        bot.edit_message_text(f"☢️ <b>SYSTEM ERROR:</b>\n<code>{str(e)}</code>", cid, status.message_id)
    
    user_data.pop(cid, None)

# --- BOOT ---
if __name__ == '__main__':
    threading.Thread(target=run_server, daemon=True).start()
    bot.set_my_commands([types.BotCommand("start", "Main Menu")])
    logger.info("Service Started.")
    bot.infinity_polling()
