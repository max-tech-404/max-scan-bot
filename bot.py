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

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔎 MAX SCAN\n\n"
        "أهلاً فيك 👋\n\n"
        "📧 أرسل إيميل لفحصه ضد تسريبات البيانات المعروفة."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔎 MAX SCAN - Help\n\n"
        "/start — تشغيل البوت\n"
        "/help — المساعدة\n\n"
        "📧 أرسل أي بريد إلكتروني لفحص ظهوره "
        "ضمن قواعد بيانات التسريبات المعروفة."
    )


async def check_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()

    if not re.match(EMAIL_REGEX, email):
        await update.message.reply_text(
            "❌ البريد الإلكتروني غير صحيح.\n\n"
            "مثال:\n"
            "example@gmail.com"
        )
        return

    msg = await update.message.reply_text(
        "🔎 جاري فحص البريد...\n"
        "⏳ لحظة واحدة."
    )

    try:
        url = (
            "https://api.xposedornot.com/v1/"
            f"check-email/{email}?details=true"
        )

        response = requests.get(
            url,
            timeout=30,
        )

        if response.status_code == 429:
            await msg.edit_text(
                "⏳ تم الوصول إلى حد الطلبات المجاني مؤقتًا.\n"
                "جرّب مرة ثانية لاحقًا."
            )
            return

        if response.status_code != 200:
            await msg.edit_text(
                f"❌ تعذر إجراء الفحص.\n"
                f"HTTP: {response.status_code}"
            )
            return

        data = response.json()

        # لم يتم العثور على البريد
        if data.get("Error") == "Not found":
            await msg.edit_text(
                "✅ النتيجة نظيفة!\n\n"
                f"📧 {email}\n\n"
                "لم يتم العثور على البريد ضمن "
                "قواعد بيانات التسريبات المعروفة."
            )
            return

        breaches = data.get("breaches", [])

        # ترتيب أسماء التسريبات
        breach_names = []

        if breaches:
            for item in breaches:
                if isinstance(item, list):
                    breach_names.extend(str(x) for x in item)
                elif isinstance(item, str):
                    breach_names.append(item)

        # إزالة التكرار
        breach_names = list(dict.fromkeys(breach_names))

        if not breach_names:
            await msg.edit_text(
                "✅ لم يتم العثور على تسريبات معروفة.\n\n"
                f"📧 {email}"
            )
            return

        text = (
            "⚠️ MAX SCAN RESULT\n\n"
            f"📧 البريد:\n{email}\n\n"
            f"🚨 عدد التسريبات: {len(breach_names)}\n\n"
            "📂 التسريبات:\n"
        )

        for i, breach in enumerate(breach_names, 1):
            text += f"{i}. {breach}\n"

        text += (
            "\n🛡️ نصيحة:\n"
            "إذا كنت تستخدم كلمة مرور مشابهة في أكثر من موقع، "
            "غيّرها فورًا وفعّل المصادقة الثنائية."
        )

        # Telegram message limit
        if len(text) > 4000:
            text = text[:3900] + "\n\n... تم اختصار النتائج."

        await msg.edit_text(text)

    except requests.Timeout:
        await msg.edit_text(
            "⏱️ انتهت مهلة الاتصال.\n"
            "جرّب مرة ثانية."
        )

    except requests.RequestException:
        await msg.edit_text(
            "❌ حدث خطأ أثناء الاتصال بخدمة الفحص."
        )

    except Exception as e:
        print("ERROR:", e)

        await msg.edit_text(
            "❌ حدث خطأ غير متوقع أثناء الفحص."
        )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("help", help_command)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            check_email
        )
    )

    print("MAX SCAN is running...")

    app.run_polling()


if __name__ == "__main__":
    main()