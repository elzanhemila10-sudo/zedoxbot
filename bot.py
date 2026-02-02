import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os
import time

# =======================
# 🔥 ZEDOX BOT CONFIG
# =======================
TOKEN = "8485630513:AAGsNguBwReji2mtQ9TjzJ26o_Xhn3oRXI0"
ADMIN_ID = 6555089031

bot = telebot.TeleBot(TOKEN, threaded=True)

USERS_FILE = "users.json"
BUTTONS_FILE = "buttons.json"
CONFIG_FILE = "config.json"

REFERRAL_BONUS = 10
PAGE_SIZE = 10


# =======================
# ✅ SAFE SEND HELPERS (FIX 403 BLOCK ERROR)
# =======================
def safe_send_message(chat_id, text, **kwargs):
    try:
        return bot.send_message(chat_id, text, **kwargs)
    except Exception as e:
        print(f"[SAFE_SEND_MESSAGE ERROR] {e}")
        return None


def safe_copy_message(chat_id, from_chat_id, message_id, **kwargs):
    try:
        return bot.copy_message(chat_id=chat_id, from_chat_id=from_chat_id, message_id=message_id, **kwargs)
    except Exception as e:
        print(f"[SAFE_COPY_MESSAGE ERROR] {e}")
        return None


def safe_answer_callback(call_id, text=""):
    try:
        bot.answer_callback_query(call_id, text)
    except:
        pass


def notify_admin(text):
    safe_send_message(ADMIN_ID, text, parse_mode="Markdown")


# =======================
# 📌 JSON HELPERS
# =======================
def load_json(filename, default_data):
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump(default_data, f, indent=4)
        return default_data
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        return default_data


def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


# =======================
# 📦 LOAD DATA
# =======================
users_data = load_json(USERS_FILE, {})
buttons_data = load_json(BUTTONS_FILE, {})

config_data = load_json(CONFIG_FILE, {
    "welcome_message": (
        "🔥🔥🔥 *WELCOME TO ZEDOX BOT* 🔥🔥🔥\n\n"
        "🚀 *THE BEST FILES & APPS STORE*\n"
        "📁 *PREMIUM • MOD • TOOLS • VIDEOS*\n\n"
        "💎 *HOW IT WORKS?*\n"
        "🎁 Invite Friends = Earn Points\n"
        "💰 Use Points = Get Files\n"
        "🆓 Some Files are FREE 😍\n\n"
        "⚡ *FAST DELIVERY • CLEAN SYSTEM*\n\n"
        "👇 Choose an option below 👇"
    ),

    "contact_text": "📞 Contact Zedox",
    "contact_url": "https://t.me/zedoxprime",

    "pro_text": "⭐ Buy PRO (No Points)",
    "pro_url": "https://t.me/zedoxprime",

    "required_joins": [
        {"username": "@zedoxtipsandtricks", "link": "https://t.me/zedoxtipsandtricks"}
    ]
})


# =======================
# 🧠 STATES
# =======================
state = {
    "autosave": {},
    "edit_price": {},
    "broadcast": False,
    "give_points_mode": False,
    "set_points_mode": False,
    "set_contact_url": False,
    "set_contact_text": False,
    "set_pro_url": False,
    "set_pro_text": False,
    "set_welcome": False,
    "add_join": False,
    "users_list_page": 0
}


# =======================
# 🧾 COMMANDS MENU
# =======================
try:
    bot.set_my_commands([
        telebot.types.BotCommand("start", "Start the bot"),
        telebot.types.BotCommand("files", "View Files / Apps"),
        telebot.types.BotCommand("balance", "My Points"),
        telebot.types.BotCommand("refer", "Referral Link"),
        telebot.types.BotCommand("id", "Show my user id + chat id"),
        telebot.types.BotCommand("chatid", "Show chat id"),
        telebot.types.BotCommand("settings", "Admin Panel"),
    ])
except:
    pass


# =======================
# 👤 USER HELPERS
# =======================
def is_admin(user_id):
    return user_id == ADMIN_ID


def ensure_user(user_id, username=""):
    uid = str(user_id)
    new_user = False

    if uid not in users_data:
        users_data[uid] = {
            "points": 0,
            "referred_by": None,
            "username": username,
            "joined_time": int(time.time())
        }
        save_json(USERS_FILE, users_data)
        new_user = True

    return new_user


def get_points(user_id):
    ensure_user(user_id)
    return int(users_data[str(user_id)]["points"])


def add_points(user_id, pts):
    ensure_user(user_id)
    users_data[str(user_id)]["points"] += int(pts)
    save_json(USERS_FILE, users_data)


def set_points(user_id, pts):
    ensure_user(user_id)
    users_data[str(user_id)]["points"] = int(pts)
    save_json(USERS_FILE, users_data)


# =======================
# 🔒 FORCE JOIN SYSTEM
# =======================
def get_required_joins():
    joins = config_data.get("required_joins", [])
    if not isinstance(joins, list):
        joins = []
    return joins


def is_user_joined_target(user_id, target_username):
    try:
        member = bot.get_chat_member(target_username, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


def check_user_join_all(user_id):
    not_joined = []
    for item in get_required_joins():
        username = (item.get("username") or "").strip()
        link = (item.get("link") or "").strip()

        if not username.startswith("@"):
            continue

        if not is_user_joined_target(user_id, username):
            not_joined.append({"username": username, "link": link})
    return not_joined


def join_required_markup(not_joined_list):
    kb = InlineKeyboardMarkup()
    for item in not_joined_list:
        kb.add(InlineKeyboardButton(f"✅ Join {item['username']}", url=item["link"]))
    kb.add(InlineKeyboardButton("🔄 I Joined", callback_data="check_join"))
    return kb


def send_join_required(chat_id, user_id):
    not_joined = check_user_join_all(user_id)
    if not not_joined:
        return False

    msg = "🚫 *ACCESS DENIED!*\n\n⚠️ Join ALL required channels/groups:\n\n"
    for item in not_joined:
        msg += f"➡️ {item['username']}\n"
    msg += "\n✅ After joining press *I Joined*"

    safe_send_message(chat_id, msg, parse_mode="Markdown", reply_markup=join_required_markup(not_joined))
    return True


# =======================
# 🎨 MENUS
# =======================
def main_menu_markup(user_id):
    kb = InlineKeyboardMarkup()

    kb.row(
        InlineKeyboardButton("📁 FILES", callback_data="menu_files"),
        InlineKeyboardButton("💰 BALANCE", callback_data="menu_balance")
    )
    kb.row(
        InlineKeyboardButton("🎁 REFERRAL", callback_data="menu_refer"),
        InlineKeyboardButton("🆔 CHAT ID", callback_data="menu_chatid")
    )
    kb.row(
        InlineKeyboardButton(config_data.get("pro_text", "⭐ Buy PRO"), url=config_data.get("pro_url", "https://t.me/zedoxprime")),
        InlineKeyboardButton(config_data.get("contact_text", "📞 Contact"), url=config_data.get("contact_url", "https://t.me/zedoxprime"))
    )

    if is_admin(user_id):
        kb.row(InlineKeyboardButton("⚙️ ADMIN PANEL", callback_data="menu_admin"))

    return kb


def admin_panel_markup():
    kb = InlineKeyboardMarkup()

    kb.row(
        InlineKeyboardButton("📥 Auto Save File", callback_data="admin_autosave_help"),
        InlineKeyboardButton("📦 Products List", callback_data="admin_product_list")
    )
    kb.row(
        InlineKeyboardButton("✏️ Edit Price", callback_data="admin_edit_price_click"),
        InlineKeyboardButton("🗑 Delete Product", callback_data="admin_delete_click")
    )
    kb.row(
        InlineKeyboardButton("➕ Give Points", callback_data="admin_give_points"),
        InlineKeyboardButton("✏️ Set Points", callback_data="admin_set_points")
    )
    kb.row(
        InlineKeyboardButton("👥 Users List", callback_data="admin_users_list"),
        InlineKeyboardButton("👥 Total Users", callback_data="admin_total_users")
    )
    kb.row(
        InlineKeyboardButton("📝 Edit Welcome", callback_data="admin_set_welcome"),
        InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
    )
    kb.row(
        InlineKeyboardButton("📌 Join List", callback_data="admin_join_list"),
        InlineKeyboardButton("➕ Add Join", callback_data="admin_add_join")
    )
    kb.row(
        InlineKeyboardButton("📞 Contact URL", callback_data="admin_set_contact_url"),
        InlineKeyboardButton("✏️ Contact Text", callback_data="admin_set_contact_text")
    )
    kb.row(
        InlineKeyboardButton("⭐ PRO URL", callback_data="admin_set_pro_url"),
        InlineKeyboardButton("✏️ PRO Text", callback_data="admin_set_pro_text")
    )
    kb.row(
        InlineKeyboardButton("⬅️ Back", callback_data="back_main")
    )

    return kb


# =======================
# 📁 FILES LIST
# =======================
def show_files(chat_id, page=0):
    products = sorted(list(buttons_data.keys()))
    if not products:
        safe_send_message(chat_id, "📁 No files yet.\n\n⚙️ Admin: Forward file from private channel to save.")
        return

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    page_items = products[start:end]

    kb = InlineKeyboardMarkup()
    row = []

    for name in page_items:
        price = int(buttons_data[name].get("price", 0))
        label = f"{name} 🆓" if price == 0 else f"{name} ({price}💰)"
        row.append(InlineKeyboardButton(label, callback_data=f"buy_{name}"))

        if len(row) == 2:
            kb.row(row[0], row[1])
            row = []

    if len(row) == 1:
        kb.row(row[0])

    if end < len(products):
        kb.row(InlineKeyboardButton("➕ MORE FILES", callback_data=f"more_{page+1}"))

    kb.row(InlineKeyboardButton("⬅️ BACK MENU", callback_data="back_main"))

    safe_send_message(chat_id, "📁 *FILES / APPS*\n\nChoose below 👇", parse_mode="Markdown", reply_markup=kb)


def send_product_file(chat_id, name):
    try:
        item = buttons_data[name]
        res = safe_copy_message(
            chat_id=chat_id,
            from_chat_id=int(item["channel_id"]),
            message_id=int(item["message_id"])
        )
        return res is not None
    except:
        safe_send_message(chat_id, "❌ Failed sending file.\n⚙️ Admin: Make bot ADMIN in storage channel.")
        return False


def buy_product(chat_id, user_id, name):
    if name not in buttons_data:
        safe_send_message(chat_id, "❌ File not found.")
        return

    price = int(buttons_data[name].get("price", 0))

    # FREE
    if price == 0:
        ok = send_product_file(chat_id, name)
        if ok:
            notify_admin(f"🆓 *FREE FILE SENT*\n👤 User: `{user_id}`\n📦 File: *{name}*")
        return

    # PAID
    if get_points(user_id) < price:
        safe_send_message(chat_id, f"❌ Not enough points!\n\n💰 Your Points: {get_points(user_id)}\n📌 Required: {price}")
        return

    users_data[str(user_id)]["points"] -= price
    save_json(USERS_FILE, users_data)

    ok = send_product_file(chat_id, name)
    if ok:
        safe_send_message(chat_id, f"✅ Success!\n💰 Remaining Points: {get_points(user_id)}")
        notify_admin(
            f"💰 *PRODUCT PURCHASE*\n"
            f"👤 User: `{user_id}`\n"
            f"📦 File: *{name}*\n"
            f"💳 Price: `{price}` pts\n"
            f"💰 Balance: `{get_points(user_id)}` pts"
        )
    else:
        users_data[str(user_id)]["points"] += price
        save_json(USERS_FILE, users_data)
        safe_send_message(chat_id, "❌ Failed! Points refunded ✅")


# =======================
# 👑 ADMIN LISTS
# =======================
def admin_send_product_list(chat_id):
    if not buttons_data:
        safe_send_message(chat_id, "📦 No products saved yet.")
        return

    msg = "📦 *PRODUCTS LIST*\n\n"
    for name, info in buttons_data.items():
        price = int(info.get("price", 0))
        msg += f"• `{name}` → {'FREE' if price == 0 else str(price)+' pts'}\n"

    safe_send_message(chat_id, msg, parse_mode="Markdown")


def admin_send_delete_list(chat_id):
    if not buttons_data:
        safe_send_message(chat_id, "📦 No products to delete.")
        return

    kb = InlineKeyboardMarkup()
    for name in buttons_data.keys():
        kb.add(InlineKeyboardButton(f"🗑 Delete {name}", callback_data=f"delprod_{name}"))

    safe_send_message(chat_id, "🗑 Select product to delete:", reply_markup=kb)


def admin_send_editprice_list(chat_id):
    if not buttons_data:
        safe_send_message(chat_id, "📦 No products to edit.")
        return

    kb = InlineKeyboardMarkup()
    for name, info in buttons_data.items():
        price = int(info.get("price", 0))
        kb.add(InlineKeyboardButton(f"✏️ {name} ({price})", callback_data=f"editprice_{name}"))

    safe_send_message(chat_id, "✏️ Select product to edit price:", reply_markup=kb)


def admin_send_users_list(chat_id, page=0):
    all_users = sorted(users_data.items(), key=lambda x: x[1].get("joined_time", 0), reverse=True)
    if not all_users:
        safe_send_message(chat_id, "👥 No users yet.")
        return

    per_page = 10
    start = page * per_page
    end = start + per_page
    chunk = all_users[start:end]

    msg = "👥 *LATEST USERS*\n\n"
    for uid, info in chunk:
        username = info.get("username") or "NoUsername"
        points = info.get("points", 0)
        msg += f"• `{uid}` | @{username} | {points} pts\n"

    kb = InlineKeyboardMarkup()
    if end < len(all_users):
        kb.row(InlineKeyboardButton("➡️ Next", callback_data=f"users_next_{page+1}"))
    if page > 0:
        kb.row(InlineKeyboardButton("⬅️ Prev", callback_data=f"users_prev_{page-1}"))
    kb.row(InlineKeyboardButton("⬅️ Back", callback_data="menu_admin"))

    safe_send_message(chat_id, msg, parse_mode="Markdown", reply_markup=kb)


# =======================
# 🚀 START
# =======================
@bot.message_handler(commands=["start"])
def start_cmd(message):
    user_id = message.from_user.id
    username = message.from_user.username or ""

    new_user = ensure_user(user_id, username)

    # Notify admin for new user
    if new_user:
        notify_admin(f"🆕 *NEW USER STARTED BOT*\n👤 User ID: `{user_id}`\n👤 Username: @{username}")

    # referral
    args = message.text.split()
    if len(args) > 1:
        ref_id = args[1]
        if ref_id.isdigit() and ref_id != str(user_id):
            if users_data[str(user_id)]["referred_by"] is None:
                users_data[str(user_id)]["referred_by"] = ref_id
                save_json(USERS_FILE, users_data)

                add_points(int(ref_id), REFERRAL_BONUS)

                notify_admin(
                    f"🎁 *NEW REFERRAL*\n"
                    f"👤 New User: `{user_id}`\n"
                    f"🏆 Referrer: `{ref_id}`\n"
                    f"➕ Bonus: `{REFERRAL_BONUS}` pts"
                )

    if send_join_required(message.chat.id, user_id):
        return

    welcome = config_data.get("welcome_message", "WELCOME!")
    safe_send_message(
        message.chat.id,
        f"{welcome}\n\n💰 *Your Points:* {get_points(user_id)}",
        parse_mode="Markdown",
        reply_markup=main_menu_markup(user_id)
    )


# =======================
# 📌 COMMANDS
# =======================
@bot.message_handler(commands=["files"])
def files_cmd(message):
    user_id = message.from_user.id
    if send_join_required(message.chat.id, user_id):
        return
    show_files(message.chat.id, page=0)


@bot.message_handler(commands=["balance"])
def balance_cmd(message):
    user_id = message.from_user.id
    if send_join_required(message.chat.id, user_id):
        return
    safe_send_message(message.chat.id, f"💰 Your Points: *{get_points(user_id)}*", parse_mode="Markdown")


@bot.message_handler(commands=["refer"])
def refer_cmd(message):
    user_id = message.from_user.id
    if send_join_required(message.chat.id, user_id):
        return
    bot_username = bot.get_me().username
    safe_send_message(
        message.chat.id,
        "🎁 *YOUR REFERRAL LINK:*\n"
        f"https://t.me/{bot_username}?start={user_id}\n\n"
        f"✅ Each referral = +{REFERRAL_BONUS} points",
        parse_mode="Markdown"
    )


@bot.message_handler(commands=["id"])
def id_cmd(message):
    safe_send_message(
        message.chat.id,
        f"🆔 *Your User ID:* `{message.from_user.id}`\n💬 *Chat ID:* `{message.chat.id}`",
        parse_mode="Markdown"
    )


@bot.message_handler(commands=["chatid"])
def chatid_cmd(message):
    safe_send_message(message.chat.id, f"💬 *Chat ID:* `{message.chat.id}`", parse_mode="Markdown")


@bot.message_handler(commands=["settings"])
def settings_cmd(message):
    if message.from_user.id != ADMIN_ID:
        safe_send_message(message.chat.id, "⚠️ Admin only.")
        return
    safe_send_message(message.chat.id, "⚙️ *ADMIN PANEL*", parse_mode="Markdown", reply_markup=admin_panel_markup())


# =======================
# 🧷 CALLBACKS
# =======================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    # Join check
    if call.data == "check_join":
        not_joined = check_user_join_all(user_id)
        if not not_joined:
            safe_answer_callback(call.id, "✅ Verified! Now type /start")
            safe_send_message(chat_id, "✅ Verified! Now type /start")
        else:
            safe_answer_callback(call.id, "❌ Join all required first!")
        return

    # Block if not joined
    not_joined = check_user_join_all(user_id)
    if not_joined:
        safe_answer_callback(call.id, "⚠️ Join required first!")
        safe_send_message(chat_id, "Please join all required:", reply_markup=join_required_markup(not_joined))
        return

    # USER MENU
    if call.data == "menu_files":
        show_files(chat_id, page=0)
        return

    if call.data == "menu_balance":
        safe_send_message(chat_id, f"💰 Your Points: *{get_points(user_id)}*", parse_mode="Markdown")
        return

    if call.data == "menu_refer":
        bot_username = bot.get_me().username
        safe_send_message(chat_id, f"🎁 Your referral:\nhttps://t.me/{bot_username}?start={user_id}")
        return

    if call.data == "menu_chatid":
        safe_send_message(chat_id, f"💬 Chat ID: `{chat_id}`\n🆔 User ID: `{user_id}`", parse_mode="Markdown")
        return

    if call.data == "back_main":
        safe_send_message(chat_id, "🏠 *MAIN MENU*", parse_mode="Markdown", reply_markup=main_menu_markup(user_id))
        return

    # Pagination
    if call.data.startswith("more_"):
        page = int(call.data.split("_")[1])
        show_files(chat_id, page=page)
        return

    # Buy product
    if call.data.startswith("buy_"):
        name = call.data.replace("buy_", "", 1)
        buy_product(chat_id, user_id, name)
        return

    # ADMIN PANEL
    if call.data == "menu_admin":
        if not is_admin(user_id):
            return
        safe_send_message(chat_id, "⚙️ *ADMIN PANEL*", parse_mode="Markdown", reply_markup=admin_panel_markup())
        return

    if not is_admin(user_id):
        return

    # Admin buttons
    if call.data == "admin_product_list":
        admin_send_product_list(chat_id)
        return

    if call.data == "admin_delete_click":
        admin_send_delete_list(chat_id)
        return

    if call.data.startswith("delprod_"):
        name = call.data.replace("delprod_", "", 1)
        if name in buttons_data:
            del buttons_data[name]
            save_json(BUTTONS_FILE, buttons_data)
            safe_send_message(chat_id, f"✅ Deleted: {name}")
        else:
            safe_send_message(chat_id, "❌ Not found.")
        return

    if call.data == "admin_edit_price_click":
        admin_send_editprice_list(chat_id)
        return

    if call.data.startswith("editprice_"):
        name = call.data.replace("editprice_", "", 1)
        if name not in buttons_data:
            safe_send_message(chat_id, "❌ Product not found.")
            return
        state["edit_price"][user_id] = name
        safe_send_message(chat_id, f"💰 Send NEW price for *{name}* (0 = FREE):", parse_mode="Markdown")
        return

    if call.data == "admin_users_list":
        admin_send_users_list(chat_id, page=0)
        return

    if call.data.startswith("users_next_"):
        page = int(call.data.split("_")[2])
        admin_send_users_list(chat_id, page=page)
        return

    if call.data.startswith("users_prev_"):
        page = int(call.data.split("_")[2])
        admin_send_users_list(chat_id, page=page)
        return

    if call.data == "admin_autosave_help":
        safe_send_message(
            chat_id,
            "📥 *AUTO SAVE PRODUCT*\n\n"
            "✅ Upload file/video in PRIVATE channel\n"
            "✅ Make bot ADMIN in that channel\n"
            "✅ Forward that message here\n\n"
            "💡 Price = 0 means FREE file 😍",
            parse_mode="Markdown"
        )
        return

    if call.data == "admin_set_welcome":
        state["set_welcome"] = True
        safe_send_message(chat_id, "📝 Send NEW welcome message now:")
        return

    if call.data == "admin_give_points":
        state["give_points_mode"] = True
        state["set_points_mode"] = False
        safe_send_message(chat_id, "➕ Send: `user_id points`\nExample: `123456789 50`", parse_mode="Markdown")
        return

    if call.data == "admin_set_points":
        state["set_points_mode"] = True
        state["give_points_mode"] = False
        safe_send_message(chat_id, "✏️ Send: `user_id points`\nExample: `123456789 200`", parse_mode="Markdown")
        return

    if call.data == "admin_broadcast":
        state["broadcast"] = True
        safe_send_message(chat_id, "📢 Send broadcast message now:")
        return

    if call.data == "admin_total_users":
        safe_send_message(chat_id, f"👥 Total Users: {len(users_data)}")
        return

    if call.data == "admin_set_contact_url":
        state["set_contact_url"] = True
        safe_send_message(chat_id, "📞 Send new contact URL:")
        return

    if call.data == "admin_set_contact_text":
        state["set_contact_text"] = True
        safe_send_message(chat_id, "✏️ Send new contact button text:")
        return

    if call.data == "admin_set_pro_url":
        state["set_pro_url"] = True
        safe_send_message(chat_id, "⭐ Send new PRO URL:")
        return

    if call.data == "admin_set_pro_text":
        state["set_pro_text"] = True
        safe_send_message(chat_id, "✏️ Send new PRO text:")
        return

    if call.data == "admin_join_list":
        req = get_required_joins()
        if not req:
            safe_send_message(chat_id, "📌 No join requirements.")
            return
        msg = "📌 *JOIN REQUIRED LIST*\n\n"
        for x in req:
            msg += f"➡️ `{x['username']}`\n"
        safe_send_message(chat_id, msg, parse_mode="Markdown")
        return

    if call.data == "admin_add_join":
        state["add_join"] = True
        safe_send_message(chat_id, "➕ Send:\n`@username | https://t.me/username`", parse_mode="Markdown")
        return


# =======================
# 📥 AUTO SAVE FILE (ADMIN FORWARD)
# =======================
@bot.message_handler(func=lambda m: m.chat.type == "private", content_types=["document", "video", "photo", "audio"])
def autosave_forward(message):
    if message.from_user.id != ADMIN_ID:
        return

    if not message.forward_from_chat or not message.forward_from_message_id:
        safe_send_message(message.chat.id, "❌ Forward from PRIVATE channel only.")
        return

    state["autosave"][ADMIN_ID] = {
        "step": "name",
        "channel_id": message.forward_from_chat.id,
        "message_id": message.forward_from_message_id
    }
    safe_send_message(message.chat.id, "✅ File received!\n📝 Now send *Product Name*:", parse_mode="Markdown")


@bot.message_handler(func=lambda m: m.from_user.id in state["autosave"] and m.chat.type == "private", content_types=["text"])
def autosave_steps(message):
    s = state["autosave"][ADMIN_ID]
    txt = message.text.strip()

    if s["step"] == "name":
        s["name"] = txt
        s["step"] = "price"
        state["autosave"][ADMIN_ID] = s
        safe_send_message(message.chat.id, "💰 Now send *Price* (0 = FREE):", parse_mode="Markdown")
        return

    if s["step"] == "price":
        try:
            price = int(txt)
            if price < 0:
                raise ValueError
        except:
            safe_send_message(message.chat.id, "❌ Send number only.")
            return

        buttons_data[s["name"]] = {
            "price": price,
            "channel_id": s["channel_id"],
            "message_id": s["message_id"]
        }
        save_json(BUTTONS_FILE, buttons_data)

        safe_send_message(message.chat.id, f"✅ Saved: *{s['name']}* ({'FREE' if price == 0 else str(price)+' pts'})", parse_mode="Markdown")
        notify_admin(f"📥 *NEW PRODUCT ADDED*\n📦 *{s['name']}*\n💰 Price: `{price}` pts")
        del state["autosave"][ADMIN_ID]


# =======================
# 📝 ADMIN INPUT HANDLER
# =======================
@bot.message_handler(content_types=["text"])
def admin_text(message):
    if message.from_user.id != ADMIN_ID:
        return

    txt = (message.text or "").strip()

    # edit price step
    if message.from_user.id in state["edit_price"]:
        prod = state["edit_price"][message.from_user.id]
        try:
            new_price = int(txt)
            if new_price < 0:
                raise ValueError
        except:
            safe_send_message(message.chat.id, "❌ Send valid number only.")
            return

        buttons_data[prod]["price"] = new_price
        save_json(BUTTONS_FILE, buttons_data)
        del state["edit_price"][message.from_user.id]
        safe_send_message(message.chat.id, f"✅ Updated: *{prod}* price = {new_price}", parse_mode="Markdown")
        notify_admin(f"✏️ *PRICE UPDATED*\n📦 {prod}\n💰 New Price: `{new_price}` pts")
        return

    if state["set_welcome"]:
        config_data["welcome_message"] = txt
        save_json(CONFIG_FILE, config_data)
        state["set_welcome"] = False
        safe_send_message(message.chat.id, "✅ Welcome message updated!")
        return

    if state["set_contact_url"]:
        config_data["contact_url"] = txt
        save_json(CONFIG_FILE, config_data)
        state["set_contact_url"] = False
        safe_send_message(message.chat.id, "✅ Contact URL updated!")
        return

    if state["set_contact_text"]:
        config_data["contact_text"] = txt
        save_json(CONFIG_FILE, config_data)
        state["set_contact_text"] = False
        safe_send_message(message.chat.id, "✅ Contact text updated!")
        return

    if state["set_pro_url"]:
        config_data["pro_url"] = txt
        save_json(CONFIG_FILE, config_data)
        state["set_pro_url"] = False
        safe_send_message(message.chat.id, "✅ PRO URL updated!")
        return

    if state["set_pro_text"]:
        config_data["pro_text"] = txt
        save_json(CONFIG_FILE, config_data)
        state["set_pro_text"] = False
        safe_send_message(message.chat.id, "✅ PRO text updated!")
        return

    if state["broadcast"]:
        sent = 0
        for uid in list(users_data.keys()):
            try:
                safe_send_message(int(uid), f"📢 *ZEDOX ANNOUNCEMENT*\n\n{txt}", parse_mode="Markdown")
                sent += 1
            except:
                pass
        state["broadcast"] = False
        safe_send_message(message.chat.id, f"✅ Broadcast done!\n📨 Sent: {sent}")
        return

    if state["add_join"]:
        try:
            parts = [x.strip() for x in txt.split("|")]
            username = parts[0]
            link = parts[1]

            if not username.startswith("@"):
                safe_send_message(message.chat.id, "❌ Username must start with @")
                return
            if not link.startswith("https://t.me/"):
                safe_send_message(message.chat.id, "❌ Link must start with https://t.me/")
                return

            config_data["required_joins"].append({"username": username, "link": link})
            save_json(CONFIG_FILE, config_data)
            state["add_join"] = False
            safe_send_message(message.chat.id, f"✅ Added join: {username}")
            return
        except:
            safe_send_message(message.chat.id, "❌ Format:\n@username | https://t.me/username")
            return

    # points
    if txt.count(" ") == 1:
        a, b = txt.split()
        if a.isdigit() and b.isdigit():
            uid = int(a)
            pts = int(b)

            if state["give_points_mode"]:
                add_points(uid, pts)
                state["give_points_mode"] = False
                safe_send_message(message.chat.id, f"✅ Added {pts} points to `{uid}`", parse_mode="Markdown")
                notify_admin(f"➕ *POINTS ADDED*\n👤 `{uid}`\n➕ `{pts}` pts")
                return

            if state["set_points_mode"]:
                set_points(uid, pts)
                state["set_points_mode"] = False
                safe_send_message(message.chat.id, f"✅ Set `{uid}` points = {pts}", parse_mode="Markdown")
                notify_admin(f"✏️ *POINTS SET*\n👤 `{uid}`\n💰 `{pts}` pts")
                return


# =======================
# ✅ RUN BOT
# =======================
print("🤖 Zedox Bot is running...")
bot.infinity_polling(skip_pending=True)