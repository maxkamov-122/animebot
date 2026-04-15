#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram import Update
from telegram.ext import ContextTypes
from database.db import get_user, create_user, update_user_phone, set_user_role
from utils import check_subscription, main_menu_keyboard, subscription_keyboard, contact_keyboard, is_admin
from config import ADMIN_IDS
from datetime import datetime

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db_user = get_user(user.id)

    # Yangi foydalanuvchi — ro'yxatdan o'tkazish
    if not db_user:
        create_user(user.id, user.username or '', user.full_name or '')
        db_user = get_user(user.id)

    # Admin ID-larini avtomatik admin qilish
    if is_admin(user.id) and db_user['role'] != 'admin':
        set_user_role(user.id, 'admin')
        db_user = get_user(user.id)

    # Telefon raqami yo'q bo'lsa so'rash
    if not db_user.get('phone'):
        await update.message.reply_text(
            "👋 Xush kelibsiz!\n\n"
            "Botdan foydalanish uchun telefon raqamingizni yuboring 👇",
            reply_markup=contact_keyboard()
        )
        return

    # Majburiy obunani tekshirish
    not_subbed = await check_subscription(context.bot, user.id)
    if not_subbed:
        await update.message.reply_text(
            "📢 Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:",
            reply_markup=subscription_keyboard(not_subbed)
        )
        return

    await show_main_menu(update, context, db_user)

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    contact = update.message.contact

    if contact.user_id != user.id:
        await update.message.reply_text("❌ Iltimos o'z raqamingizni yuboring!")
        return

    update_user_phone(user.id, contact.phone_number)

    not_subbed = await check_subscription(context.bot, user.id)
    db_user = get_user(user.id)

    if not_subbed:
        await update.message.reply_text(
            "✅ Raqam saqlandi!\n\n📢 Endi quyidagi kanallarga obuna bo'ling:",
            reply_markup=subscription_keyboard(not_subbed)
        )
        return

    await show_main_menu(update, context, db_user)

async def show_main_menu(update, context, db_user):
    role = db_user['role']
    premium_status = ""
    if db_user.get('premium_until'):
        exp = datetime.fromisoformat(db_user['premium_until'])
        if exp > datetime.now():
            premium_status = f"\n⭐ Premium: {exp.strftime('%d.%m.%Y')}"

    text = (
        f"🎌 <b>Anime Bot</b>\n\n"
        f"👤 {db_user['full_name']}\n"
        f"🔰 Rol: <b>{role.capitalize()}</b>"
        f"{premium_status}\n\n"
        f"Quyidagi tugmalardan birini tanlang:"
    )

    if update.message:
        await update.message.reply_text(text, parse_mode='HTML', reply_markup=main_menu_keyboard(role))
    else:
        await update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=main_menu_keyboard(role))
