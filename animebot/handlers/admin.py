#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.db import get_all_users, get_user, set_user_role, give_user_premium, get_channels, add_channel, remove_channel
from utils import is_admin, back_button
from config import PREMIUM_DAYS

CHANNEL_ID = 0

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("❌ Sizda admin huquqi yo'q!")
        return
    await _show_admin_panel(update, context)

async def _show_admin_panel(update, context):
    buttons = [
        [InlineKeyboardButton("👥 Foydalanuvchilar", callback_data="admin_users")],
        [InlineKeyboardButton("📢 Kanallar boshqaruvi", callback_data="admin_channels")],
        [InlineKeyboardButton("🔙 Bosh menyu", callback_data="main_menu")],
    ]
    text = "🔧 <b>Admin Panel</b>\n\nNimani qilmoqchisiz?"
    kb = InlineKeyboardMarkup(buttons)
    if update.message:
        await update.message.reply_text(text, parse_mode='HTML', reply_markup=kb)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=kb)

async def back_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _show_admin_panel(update, context)

async def admin_users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.answer("❌ Huquq yo'q!", show_alert=True)
        return

    page = int(context.user_data.get('users_page', 0))
    users, total = get_all_users(limit=10, offset=page * 10)

    buttons = []
    for u in users:
        role_icon = {"admin": "👑", "manager": "🔑", "user": "👤"}.get(u['role'], "👤")
        premium = "⭐" if u.get('premium_until') else ""
        buttons.append([InlineKeyboardButton(
            f"{role_icon}{premium} {u['full_name']} (@{u['username'] or 'nouser'})",
            callback_data=f"admin_user_{u['telegram_id']}"
        )])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️", callback_data=f"users_page_{page-1}"))
    nav.append(InlineKeyboardButton(f"{page+1}/{(total//10)+1}", callback_data="noop"))
    if (page+1)*10 < total:
        nav.append(InlineKeyboardButton("▶️", callback_data=f"users_page_{page+1}"))
    if nav:
        buttons.append(nav)
    buttons.append([InlineKeyboardButton("🔙 Admin", callback_data="back_admin")])

    await query.edit_message_text(
        f"👥 <b>Foydalanuvchilar</b> (jami: {total})",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def admin_user_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        return

    user_id = int(query.data.split('_')[-1])
    u = get_user(user_id)
    if not u:
        await query.answer("Foydalanuvchi topilmadi!", show_alert=True)
        return

    from datetime import datetime
    premium_text = "Yo'q"
    if u.get('premium_until'):
        exp = datetime.fromisoformat(u['premium_until'])
        if exp > datetime.now():
            premium_text = f"✅ {exp.strftime('%d.%m.%Y')}"
        else:
            premium_text = "❌ Muddati o'tgan"

    text = (
        f"👤 <b>Foydalanuvchi ma'lumotlari</b>\n\n"
        f"📛 Ism: {u['full_name']}\n"
        f"🆔 ID: <code>{u['telegram_id']}</code>\n"
        f"📱 Tel: {u.get('phone') or 'Yo\'q'}\n"
        f"🔰 Rol: <b>{u['role']}</b>\n"
        f"⭐ Premium: {premium_text}\n"
        f"📅 Qo'shilgan: {u['joined_at'][:10]}"
    )

    buttons = [
        [
            InlineKeyboardButton("👤 User", callback_data=f"set_role_{user_id}_user"),
            InlineKeyboardButton("🔑 Manager", callback_data=f"set_role_{user_id}_manager"),
        ],
        [InlineKeyboardButton(f"⭐ Premium berish ({PREMIUM_DAYS} kun)", callback_data=f"give_premium_{user_id}")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin_users")],
    ]

    await query.edit_message_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(buttons))

async def set_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        return

    parts = query.data.split('_')
    user_id = int(parts[2])
    role = parts[3]

    set_user_role(user_id, role)
    await query.answer(f"✅ Rol '{role}' ga o'zgartirildi!", show_alert=True)
    # Refresh detail
    context.user_data['last_user_id'] = user_id
    query.data = f"admin_user_{user_id}"
    await admin_user_detail(update, context)

async def give_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        return

    user_id = int(query.data.split('_')[-1])
    until = give_user_premium(user_id, days=PREMIUM_DAYS)
    await query.answer(f"✅ Premium {until.strftime('%d.%m.%Y')} gacha berildi!", show_alert=True)
    query.data = f"admin_user_{user_id}"
    await admin_user_detail(update, context)

# ─── CHANNEL MANAGEMENT ───────────────────────────────────

async def manage_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        return

    channels = get_channels()
    text = "📢 <b>Kanallar boshqaruvi</b>\n\n"
    buttons = []

    if channels:
        for ch in channels:
            name = ch.get('channel_name') or ch['channel_id']
            buttons.append([InlineKeyboardButton(
                f"🗑 {name}",
                callback_data=f"remove_channel_{ch['channel_id'].replace('-', 'NEG')}"
            )])
        text += f"Jami {len(channels)} ta kanal"
    else:
        text += "Hozircha kanallar yo'q."

    buttons.append([InlineKeyboardButton("➕ Kanal qo'shish", callback_data="add_channel")])
    buttons.append([InlineKeyboardButton("🔙 Admin", callback_data="back_admin")])

    await query.edit_message_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(buttons))

async def add_channel_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        return

    await query.edit_message_text(
        "📢 Kanal ID-sini yuboring:\n\n"
        "Misol: <code>@mychannelname</code> yoki <code>-1001234567890</code>\n\n"
        "/cancel — bekor qilish",
        parse_mode='HTML'
    )
    return CHANNEL_ID

async def save_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel_id = update.message.text.strip()
    try:
        chat = await context.bot.get_chat(channel_id)
        add_channel(channel_id, chat.title)
        await update.message.reply_text(f"✅ '{chat.title}' kanali qo'shildi!")
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {e}\n\nBot kanalga admin bo'lishi kerak!")
    return ConversationHandler.END

async def remove_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    channel_id = query.data.replace("remove_channel_", "").replace("NEG", "-")
    remove_channel(channel_id)
    await query.answer("✅ Kanal o'chirildi!", show_alert=True)
    await manage_channels(update, context)

async def cancel_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Bekor qilindi.")
    return ConversationHandler.END
