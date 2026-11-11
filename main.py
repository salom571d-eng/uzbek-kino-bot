
import os
import json
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("8875071130:AAH0He4wgg3QBC0q577ErVG1k6EI38Vc290")
ADMIN_ID = 7208785053
KANAL = "@kinolartop08"
KANAL_LINK = "https://t.me/kinolartop08"

if not TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

bot = telebot.TeleBot(TOKEN)
FILE = "kinolar.json"
kutish = {}

def yuklash():
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

KINOLAR = yuklash()

def saqlash():
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(KINOLAR, f, ensure_ascii=False, indent=2)

def admin(m):
    return m.from_user.id == ADMIN_ID

def obuna(uid):
    try:
        a = bot.get_chat_member(KANAL, uid)
        return a.status in ["member", "administrator", "creator"]
    except:
        return False

def tugma():
    k = InlineKeyboardMarkup()
    k.add(InlineKeyboardButton("📢 Kanalga obuna bo‘lish", url=KANAL_LINK))
    k.add(InlineKeyboardButton("✅ Tekshirish", callback_data="check"))
    return k

@bot.message_handler(commands=["start"])
def start(m):
    if not obuna(m.from_user.id):
        bot.send_message(m.chat.id, "Avval kanalga obuna bo‘ling!", reply_markup=tugma())
    else:
        bot.send_message(m.chat.id, "🎬 Kino kodini yuboring.\nMasalan: 101")

@bot.callback_query_handler(func=lambda c: c.data == "check")
def check(c):
    if obuna(c.from_user.id):
        bot.answer_callback_query(c.id, "Obuna tasdiqlandi!")
        bot.send_message(c.message.chat.id, "🎬 Kino kodini yuboring.")
    else:
        bot.answer_callback_query(c.id, "Avval obuna bo‘ling!", show_alert=True)

@bot.message_handler(commands=["myid"])
def myid(m):
    bot.reply_to(m, f"ID: {m.from_user.id}")

@bot.message_handler(commands=["add"])
def add(m):
    if admin(m):
        kutish[m.chat.id] = {"step": "code"}
        bot.reply_to(m, "Kino kodini yuboring:")

@bot.message_handler(commands=["cancel"])
def cancel(m):
    kutish.pop(m.chat.id, None)
    bot.reply_to(m, "Bekor qilindi.")

@bot.message_handler(commands=["list"])
def listing(m):
    if admin(m):
        bot.reply_to(m, "Kinolar:\n" + ("\n".join(KINOLAR.keys()) if KINOLAR else "Hozircha yo‘q"))

@bot.message_handler(commands=["delete"])
def delete(m):
    if not admin(m):
        return
    p = m.text.split(maxsplit=1)
    if len(p) != 2 or p[1] not in KINOLAR:
        bot.reply_to(m, "Masalan: /delete 101")
        return
    del KINOLAR[p[1]]
    saqlash()
    bot.reply_to(m, "Kino o‘chirildi.")

@bot.message_handler(commands=["stats"])
def stats(m):
    if admin(m):
        bot.reply_to(m, f"Jami kinolar: {len(KINOLAR)}")

@bot.message_handler(content_types=["video"])
def video(m):
    if not admin(m):
        return
    d = kutish.get(m.chat.id)
    if not d or d["step"] != "video":
        return
    KINOLAR[d["code"]] = {
        "nom": d["name"],
        "file_id": m.video.file_id
    }
    saqlash()
    kutish.pop(m.chat.id)
    bot.reply_to(m, f"✅ Kino saqlandi!\nKodi: {d['code']}")

@bot.message_handler(func=lambda m: m.text is not None)
def text_handler(m):
    if admin(m) and m.chat.id in kutish:
        d = kutish[m.chat.id]
        if d["step"] == "code":
            d["code"] = m.text.strip()
            d["step"] = "name"
            bot.reply_to(m, "Kino nomini yuboring:")
            return
        if d["step"] == "name":
            d["name"] = m.text.strip()
            d["step"] = "video"
            bot.reply_to(m, "Endi kino videosini yuboring:")
            return

    if not obuna(m.from_user.id):
        bot.send_message(m.chat.id, "Avval kanalga obuna bo‘ling!", reply_markup=tugma())
        return

    kino = KINOLAR.get(m.text.strip())
    if kino:
        if isinstance(kino, str):
            bot.send_video(m.chat.id, kino)
        else:
            bot.send_video(m.chat.id, kino["file_id"], caption=kino["nom"])
    else:
        bot.reply_to(m, "❌ Bunday kino kodi topilmadi.")

bot.infinity_polling(skip_pending=True)
    
