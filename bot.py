import os
import re
import requests

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.environ["BOT_TOKEN"]
INTELBASE_API_KEY = os.environ["INTELBASE_API_KEY"]

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔎 MAX SCAN\n\n"
        "أهلاً فيك 👋\n"
        "أرسل عنوان بريد إلكتروني لإجراء البحث."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔎 MAX SCAN\n\n"
        "الأوامر:\n"
        "/start - بدء البوت\n"
        "/help - المساعدة\n\n"
        "حالياً يدعم البحث عن البريد الإلكتروني."
    )


async def lookup_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()

    if not re.match(EMAIL_REGEX, email):
        await update.message.reply_text(
            "❌ أرسل عنوان بريد إلكتروني صحيح."
        )
        return

    await update.message.reply_text("🔎 جاري البحث...")

    try:
        response = requests.post(
            "https://api.intelbase.is/lookup/email",
            headers={
                "Content-Type": "application/json",
                "x-api-key": INTELBASE_API_KEY,
            },
            json={
                "email": email,
                "include_data_breaches": True
            },
            timeout=60,
        )

        if response.status_code == 200:
            data = response.json()

            text = (
                "🔎 MAX SCAN\n\n"
                f"📧 Email: {email}\n\n"
                f"📊 النتيجة:\n"
                f"{data}"
            )

            # تيليجرام عنده حد لطول الرسالة
            if len(text) > 4000:
                text = text[:3900] + "\n\n... تم اختصار النتيجة."

            await update.message.reply_text(text)

        else:
            await update.message.reply_text(
                f"❌ IntelBase رجّع خطأ: {response.status_code}"
            )

    except requests.Timeout:
        await update.message.reply_text(
            "⏱️ انتهت مهلة البحث، جرّب مرة ثانية."
        )

    except Exception as e:
        print("ERROR:", e)
        await update.message.reply_text(
            "❌ صار خطأ أثناء الاتصال بـ IntelBase."
        )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, lookup_email)
    )

    print("MAX SCAN is running...")
    app.run_polling()


if __name__ == "__main__":
    main()