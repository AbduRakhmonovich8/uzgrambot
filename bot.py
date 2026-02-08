from telegram import (
    Update,
    InlineKeyboardButton,
    WebAppInfo,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import users1_supabase as db  # Supabase modul nomi
import os


TOKEN = os.getenv("TOKEN")
admin_id = int(os.getenv("ADMIN_ID"))
print(f"Admin ID: {admin_id}")
print(f"Bot Token: {TOKEN   }")


# ===================== /start =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    user = db.get_user(user_id)

    if not user:
        db.create_user(user_id=user_id, username=username, isActive=True)

    user = db.get_user(user_id)
    await update.message.reply_text(
        f"Assalomu alaykum qadirli {update.effective_user.first_name}.",
        reply_markup=ReplyKeyboardRemove(),
    )

    if not user["isActive"]:
        await update.message.reply_text(
            f"Sizning holatingiz: Locked Account 🔒 \nSizning akkauntingiz bloklangan. Iltimos, admin bilan bog'laning."
        )
    else:
        await update.message.reply_text(f"Sizning holatingiz: Active Account ✅")

    if not user["number"]:
        kb = [[KeyboardButton("📞 Raqamni yuborish", request_contact=True)]]
        await update.message.reply_text(
            "Iltimos, telefon raqamingizni yuboring:",
            reply_markup=ReplyKeyboardMarkup(
                kb, resize_keyboard=True, one_time_keyboard=True
            ),
        )


# ===================== REPLY TUGMALAR =====================
async def reply_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.contact:
        phone = update.message.contact.phone_number
        user_id = update.effective_user.id
        db.update_user(user_id, number=phone)
        await update.message.reply_text(
            f"Rahmat! Raqamingiz qabul qilindi:\n{phone}",
            reply_markup=ReplyKeyboardRemove(),
        )


async def reply_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    common_texts = text.split(" ")

    if common_texts[0] == "sudo" and update.effective_user.id == admin_id:
        cmd = common_texts[1]

        if cmd == "help":
            await update.message.reply_text(
                """sudo [options] or <command><user_id>
Mavjud buyruqlar:
options:
    help - Yordam ma'lumotlarini ko'rsatadi.
    whoami - Sizning admin ekanligingizni tasdiqlaydi.
    show_users - Barcha foydalanuvchilar ro'yxatini ko'rsatadi.
    show_actives - Faol foydalanuvchilar ro'yxatini ko'rsatadi.
    show_noactives - Faol bo'lmagan foydalanuvchilar ro'yxatini ko'rsatadi.
commands:
    delete_user <user_id> - Foydalanuvchini bazadan o'chiradi.
    admin_action_on <user_id> - Foydalanuvchini activeligini yoqadi.
    admin_action_off <user_id> - Foydalanuvchini activeligini o'chiradi."""
            )
        elif cmd == "whoami":
            await update.message.reply_text("Siz admin bo'lib tasdiqlandingiz.")
        elif cmd == "show_users":
            users = db.get_all_users()
            for user in users:
                print(user)
                await update.message.reply_text(
                    text=(
                        f"User ID: {user['user_id']}\n"
                        f"Username: @{user['username']}\n"
                        f"Active: {user['isActive']}\n"
                        f"Phone: {user['number']}\n"
                        f"Two Step Verification: {user['twoStepVerify']}"
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "🗑 O‘chirish",
                                    callback_data=f"delete_{user['user_id']}",
                                )
                            ]
                        ]
                    ),
                )
        elif cmd == "show_actives":
            actives = db.get_actives()
            keyboard = [
                [
                    InlineKeyboardButton(
                        f"@{user['username']}", callback_data=f"user_{user['user_id']}"
                    ),
                    InlineKeyboardButton("🔒", callback_data=f"lock_{user['user_id']}"),
                ]
                for user in actives
            ]
            keyboard.append(
                [InlineKeyboardButton("❌ chiqish", callback_data="chiqish")]
            )
            await update.message.reply_text(
                "🔓 Active foydalanuvchilar ro'yxati:",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        elif cmd == "show_noactives":
            noactives = db.get_noactives()
            keyboard = [
                [
                    InlineKeyboardButton(
                        f"@{user['username']}", callback_data=f"user_{user['user_id']}"
                    ),
                    InlineKeyboardButton(
                        "🔑", callback_data=f"unlock_{user['user_id']}"
                    ),
                ]
                for user in noactives
            ]
            keyboard.append(
                [InlineKeyboardButton("❌ chiqish", callback_data="chiqish")]
            )
            await update.message.reply_text(
                "🔒 NoActive foydalanuvchilar ro'yxati:",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        elif cmd == "su":
            kb = [
                [
                    KeyboardButton("sudo show_users"),
                    KeyboardButton("sudo show_actives"),
                ],
                [KeyboardButton("sudo show_noactives"), KeyboardButton("sudo whoami")],
                [KeyboardButton("sudo help")],
            ]
            await update.message.reply_text(
                "Admin menyu:",
                reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True),
            )
        elif cmd == "exit":
            await update.message.reply_text(
                "Admin menyudan chiqildi.", reply_markup=ReplyKeyboardRemove()
            )
    elif common_texts[0] == "sudo":
        await update.message.reply_text("Siz admin emassiz.")


# ===================== INLINE TUGMALAR =====================
async def inline_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "chiqish":
        await query.edit_message_text("removelist", reply_markup=None)
    elif query.data.startswith("user_"):
        user_id = int(query.data.split("_")[1])
        user = db.get_user(user_id)
        if user:
            await query.edit_message_text(
                f"User ID: {user['user_id']},\nUsername: @{user['username']},\nActive: {user['isActive']},\nPhone: {user['number']},\nTwo Step Verification: {user['twoStepVerify']}"
            )
        else:
            await query.edit_message_text("Foydalanuvchi topilmadi.")
    elif query.data.startswith("unlock_"):
        user_id = int(query.data.split("_")[1])
        db.activate_user(user_id)
        await query.edit_message_text(f"Foydalanuvchi {user_id} activelashtirildi.")
    elif query.data.startswith("lock_"):
        user_id = int(query.data.split("_")[1])
        db.deactivate_user(user_id)
        await query.edit_message_text(f"Foydalanuvchi {user_id} bloklandi.")
    elif query.data.startswith("delete_"):
        user_id = int(query.data.split("_")[1])
        db.delete_user(user_id)
        await query.edit_message_text(f"Foydalanuvchi {user_id} bazadan o'chirildi.")


# ===================== MAIN =====================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(inline_menu))
    app.add_handler(MessageHandler(filters.CONTACT, reply_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_text))

    print("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
