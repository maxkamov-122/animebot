#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.db import add_anime, add_episode, get_anime_by_id, get_episodes, get_user
from config import MAX_FILE_SIZE
from utils import format_size

# States
ANIME_NAME, ANIME_PHOTO, ANIME_DESC, ANIME_PREMIUM = range(4)
EP_NUMBER, EP_TITLE, EP_VIDEO = range(10, 13)

def is_staff(user_id):
    from utils import is_admin
    if is_admin(user_id):
        return True
    u = get_user(user_id)
    return u and u['role'] in ('admin', 'manager')

async def add_anime_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_staff(query.from_user.id):
        await query.answer("❌ Huquq yo'q!", show_alert=True)
        return ConversationHandler.END

    await query.edit_message_text(
        "🎌 <b>Yangi anime qo'shish</b>\n\n"
        "1️⃣ Anime nomini yuboring:\n\n"
        "/cancel — bekor qilish",
        parse_mode='HTML'
    )
    return ANIME_NAME

async def get_anime_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['anime_name'] = update.message.text.strip()
    await update.message.reply_text(
        f"✅ Nom: <b>{context.user_data['anime_name']}</b>\n\n"
        f"2️⃣ Anime rasmini yuboring (poster):",
        parse_mode='HTML'
    )
    return ANIME_PHOTO

async def get_anime_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    context.user_data['anime_photo'] = photo.file_id
    await update.message.reply_text(
        "✅ Rasm saqlandi!\n\n"
        "3️⃣ Anime haqida qisqacha yozing (bio/tavsif):"
    )
    return ANIME_DESC

async def get_anime_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['anime_desc'] = update.message.text.strip()
    buttons = [
        [InlineKeyboardButton("⭐ Ha, Premium", callback_data="premium_yes"),
         InlineKeyboardButton("🆓 Yo'q, Bepul", callback_data="premium_no")]
    ]
    await update.message.reply_text(
        "4️⃣ Bu anime premium bo'lsinmi?",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return ANIME_PREMIUM

async def get_anime_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    is_premium = query.data == "premium_yes"
    context.user_data['anime_premium'] = is_premium

    data = context.user_data
    anime_id, code = add_anime(
        name=data['anime_name'],
        description=data['anime_desc'],
        photo_id=data['anime_photo'],
        is_premium=is_premium,
        added_by=query.from_user.id
    )

    premium_text = "⭐ PREMIUM" if is_premium else "🆓 Bepul"
    buttons = [[InlineKeyboardButton("➕ Qism qo'shish", callback_data=f"add_episode_{anime_id}")]]

    await query.edit_message_text(
        f"✅ <b>Anime qo'shildi!</b>\n\n"
        f"📛 Nom: {data['anime_name']}\n"
        f"🔢 Kod: <code>{code}</code>\n"
        f"🔰 Turi: {premium_text}\n\n"
        f"Endi qismlarni qo'shing:",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return ConversationHandler.END

async def add_episode_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_staff(query.from_user.id):
        await query.answer("❌ Huquq yo'q!", show_alert=True)
        return ConversationHandler.END

    anime_id = int(query.data.split('_')[-1])
    anime = get_anime_by_id(anime_id)
    if not anime:
        await query.answer("Anime topilmadi!", show_alert=True)
        return ConversationHandler.END

    context.user_data['ep_anime_id'] = anime_id
    context.user_data['ep_anime_name'] = anime['name']

    existing = get_episodes(anime_id)
    next_ep = len(existing) + 1

    await query.edit_message_text(
        f"🎬 <b>{anime['name']}</b>\n\n"
        f"Qism raqamini yuboring (masalan: <code>{next_ep}</code>):\n\n"
        f"/cancel — bekor qilish",
        parse_mode='HTML'
    )
    return EP_NUMBER

async def get_ep_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        ep_num = int(update.message.text.strip())
        context.user_data['ep_number'] = ep_num
        await update.message.reply_text(f"✅ Qism: {ep_num}\n\nQism nomini yuboring (masalan: 'Birinchi to\\'siq'):")
        return EP_TITLE
    except ValueError:
        await update.message.reply_text("❌ Faqat raqam kiriting!")
        return EP_NUMBER

async def get_ep_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ep_title'] = update.message.text.strip()
    await update.message.reply_text(
        f"✅ Sarlavha: {context.user_data['ep_title']}\n\n"
        f"🎬 Video faylni yuboring (maksimal: 2GB)\n\n"
        f"⚠️ Video to'g'ridan-to'g'ri Telegram orqali yuboriladi, server saqlaydi."
    )
    return EP_VIDEO

async def get_ep_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.video:
        file_obj = update.message.video
    elif update.message.document:
        file_obj = update.message.document
    else:
        await update.message.reply_text("❌ Iltimos video fayl yuboring!")
        return EP_VIDEO

    file_size = file_obj.file_size or 0
    if file_size > MAX_FILE_SIZE:
        await update.message.reply_text(
            f"❌ Fayl hajmi juda katta!\n"
            f"Maksimal: {format_size(MAX_FILE_SIZE)}\n"
            f"Yuborilgan: {format_size(file_size)}"
        )
        return EP_VIDEO

    data = context.user_data
    add_episode(
        anime_id=data['ep_anime_id'],
        episode_number=data['ep_number'],
        title=data['ep_title'],
        file_id=file_obj.file_id,
        file_size=file_size
    )

    anime = get_anime_by_id(data['ep_anime_id'])
    buttons = [
        [InlineKeyboardButton("➕ Yana qism qo'shish", callback_data=f"add_episode_{data['ep_anime_id']}")],
        [InlineKeyboardButton("🔙 Bosh menyu", callback_data="main_menu")],
    ]

    await update.message.reply_text(
        f"✅ <b>Qism qo'shildi!</b>\n\n"
        f"📛 Anime: {anime['name']}\n"
        f"🎬 Qism: {data['ep_number']} - {data['ep_title']}\n"
        f"💾 Hajm: {format_size(file_size)}",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Bekor qilindi.")
    return ConversationHandler.END
