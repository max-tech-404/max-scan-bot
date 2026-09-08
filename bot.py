import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.environ["BOT_TOKEN"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔎 MAX SCAN\n\n"
        "البوت شغال بنجاح! 🤖🔥\n"
        "قريباً رح نضيف نظام البحث."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 الأوامر:\n\n"
        "/start - تشغيل البوت\n"
        "/help - المساعدة"
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    print("MAX SCAN is running...")
    app.run_polling()


if __name__ == "__main__":
    main()