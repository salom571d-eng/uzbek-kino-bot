
import os
import json
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# SOZLAMALAR
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7208785053
KANAL = "@kinolartop08"
KANAL_LINK = "https://t.me/kinolartop08"

if not TOKEN:
    raise ValueError("Render Environment ichida BOT_TOKEN yo'q!")

bot = telebot.TeleBot(TOKEN)

FILE = "kinolar.json"
KINOLAR = {}
HOLAT = {}

# KINOLARNI YUKLASH
def yuklash():
    global KINOLAR
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            KINOLAR = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        KINOLAR = {}

def saqlash():
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(KINOLAR, f, ensure_ascii=False, indent=2)

yuklash()

# ADMIN TEKSHIRISH
def admin(message):
    return message.from_user.id == ADMIN_ID

# OBUNA TEKSHIRISH
def obuna(uid):
    try:
        member = bot.get_chat_member(KANAL, uid)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

def obuna_tugma():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📢 Kanalga obuna bo'lish", url=KANAL_LINK)
    )
    markup.add(
        InlineKeyboardButton("✅ Tekshirish", callback_data="tekshir")
    )
    return markup

# START
@bot.message_handler(commands=["start"])
def start(message):
    if not obuna(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "🎬 Botdan foydalanish uchun kanalga obuna bo'ling!",
            reply_markup=obuna_tugma()
        )
        return

    bot.send_message(
        message.chat.id,
        "🎬 Uzbek Kino Olami!\n\n"
        "Kino kodini yuboring.\n"
        "Masalan: 101"
    )

# OBUNANI TEKSHIRISH
@bot.callback_query_handler(func=lambda call: call.data == "tekshir")
def tekshir(call):
    if obuna(call.from_user.id):
        bot.answer_callback_query(call.id, "Obuna tasdiqlandi!")
        bot.send_message(
            call.message.chat.id,
            "✅ Obuna tasdiqlandi!\nKino kodini yuboring."
        )
    else:
        bot.answer_callback_query(
            call.id,
            "Avval kanalga obuna bo'ling!",
            show_alert=True
        )

# ADMIN ID
@bot.message_handler(commands=["myid"])
def myid(message):
    bot.reply_to(message, f"Sizning ID: {message.from_user.id}")

# KINO QO'SHISH
@bot.message_handler(commands=["add"])
def add(message):
    if not admin(message):
        return

    HOLAT[message.chat.id] = {"step": "kod"}
    bot.reply_to(message, "📝 Kino kodini yuboring:")

# KINO VIDEOSINI QABUL QILISH
@bot.message_handler(content_types=["video"])
def video_qabul(message):
    if not admin(message):
        return

    data = HOLAT.get(message.chat.id)

    if not data or data["step"] != "video":
        return

    kod = data["kod"]
    nom = data["nom"]

    KINOLAR[kod] = {
        "nom": nom,
        "file_id": message.video.file_id
    }

    saqlash()
    HOLAT.pop(message.chat.id, None)

    bot.reply_to(
        message,
        f"✅ Kino saqlandi!\n\n🎬 Nomi: {nom}\n🔢 Kodi: {kod}"
    )

# KINO RO'YXATI
@bot.message_handler(commands=["list"])
def royxat(message):
    if not admin(message):
        return

    if not KINOLAR:
        bot.reply_to(message, "Hozircha kino yo'q.")
        return

    matn = "🎬 Kinolar ro'yxati:\n\n"
    for kod, kino in KINOLAR.items():
        matn += f"🔢 {kod} — {kino['nom']}\n"

    bot.reply_to(message, matn)

# KINO O'CHIRISH
@bot.message_handler(commands=["delete"])
def ochirish(message):
    if not admin(message):
        return

    qismlar = message.text.split(maxsplit=1)

    if len(qismlar) < 2:
        bot.reply_to(message, "Masalan: /delete 101")
        return

    kod = qismlar[1].strip()

    if kod not in KINOLAR:
        bot.reply_to(message, "Bunday kino topilmadi.")
        return

    del KINOLAR[kod]
    saqlash()
    bot.reply_to(message, "🗑 Kino o'chirildi.")

# STATISTIKA
@bot.message_handler(commands=["stats"])
def statistika(message):
    if admin(message):
        bot.reply_to(message, f"Jami kinolar: {len(KINOLAR)} ta")

# BEKOR QILISH
@bot.message_handler(commands=["cancel"])
def bekor(message):
    HOLAT.pop(message.chat.id, None)
    bot.reply_to(message, "❌ Amal bekor qilindi.")

# MATNLARNI QABUL QILISH
@bot.message_handler(func=lambda m: m.text is not None)
def matn(message):
    chat_id = message.chat.id
    uid = message.from_user.id
    text = message.text.strip()

    # ADMIN KINO QO'SHAYOTGAN BO'LSA
    if admin(message) and chat_id in HOLAT:
        data = HOLAT[chat_id]

        if data["step"] == "kod":
            data["kod"] = text
            data["step"] = "nom"
            bot.reply_to(message, "🎬 Kino nomini yuboring:")
            return

        if data["step"] == "nom":
            data["nom"] = text
            data["step"] = "video"
            bot.reply_to(message, "📹 Endi kino videosini yuboring:")
            return

        if data["step"] == "video":
            bot.reply_to(message, "Iltimos, kino videosini yuboring.")
            return

    # FOYDALANUVCHI OBUNASINI TEKSHIRISH
    if not obuna(uid):
        bot.send_message(
            chat_id,
            "Avval kanalga obuna bo'ling!",
            reply_markup=obuna_tugma()
        )
        return

    # KINO QIDIRISH
    kino = KINOLAR.get(text)

    if kino:
        bot.send_video(
            chat_id,
            kino["file_id"],
            caption=f"🎬 {kino['nom']}\n\n🍿 Yoqimli tomosha!"
        )
    else:
        bot.reply_to(message, "❌ Bunday kino kodi topilmadi.")

print("BOT ISHGA TUSHDI!")
bot.infinity_polling(skip_pending=True)
            
