#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import get_user, is_premium
from datetime import datetime

async def my_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    u = get_user(user_id)
    if not u:
        await query.answer("Foydalanuvchi topilmadi!", show_alert=True)
        return

    premium_status = "❌ Yo'q"
    if u['role'] in ('admin', 'manager'):
        premium_status = "♾️ Cheksiz (rol orqali)"
    elif u.get('premium_until'):
        exp = datetime.fromisoformat(u['premium_until'])
        if exp > datetime.now():
            days_left = (exp - datetime.now()).days
            premium_status = f"✅ {exp.strftime('%d.%m.%Y')} ({days_left} kun qoldi)"
        else:
            premium_status = "❌ Muddati tugagan"

    role_icons = {"admin": "👑 Admin", "manager": "🔑 Manager", "user": "👤 Oddiy foydalanuvchi"}
    role_text = role_icons.get(u['role'], u['role'])

    text = (
        f"👤 <b>Mening profilim</b>\n\n"
        f"📛 Ism: {u['full_name']}\n"
        f"🆔 Telegram ID: <code>{u['telegram_id']}</code>\n"
        f"📱 Tel: {u.get('phone') or 'Kiritilmagan'}\n"
        f"🔰 Rol: <b>{role_text}</b>\n"
        f"⭐ Premium: {premium_status}\n"
        f"📅 Ro'yxatdan: {u['joined_at'][:10]}"
    )

    from config import PREMIUM_CONTACT
    buttons = []
    if u['role'] == 'user' and not is_premium(user_id):
        buttons.append([InlineKeyboardButton(f"⭐ Premium olish → {PREMIUM_CONTACT}", url=f"https://t.me/{PREMIUM_CONTACT.lstrip('@')}")])
    buttons.append([InlineKeyboardButton("🔙 Bosh menyu", callback_data="main_menu")])

    await query.edit_message_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(buttons))
