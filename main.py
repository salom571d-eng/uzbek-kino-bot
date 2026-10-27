
import os
import telebot

TOKEN = os.environ["BOT_TOKEN"]
bot = telebot.TeleBot(TOKEN)

KINOLAR = {
    "101": "BAACAgIAAxkBAAMiauBfj0rJaiuHwEbXY9Std0IP6aUAAvunAAKLIwFLrtaG0vSLFIw9BA"
}

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "🎬 Uzbek Kino Olami!\n\nKino kodini yuboring.\nMasalan: 101"
    )

@bot.message_handler(func=lambda message: message.text is not None)
def kino_top(message):
    kod = message.text.strip()
    if kod in KINOLAR:
        bot.send_video(message.chat.id, KINOLAR[kod])
    else:
        bot.reply_to(message, "❌ Bunday kino kodi topilmadi.")

bot.infinity_polling()
