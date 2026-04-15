#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import search_animes, get_premium_animes, get_anime_by_id, get_episodes, get_episode, is_premium
from utils import main_menu_keyboard, back_button
from config import PREMIUM_CONTACT
from database.db import get_user

SEARCH_MODE = {}  # user_id -> mode ('name' or 'code')

async def search_by_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    SEARCH_MODE[query.from_user.id] = 'name'
    await query.edit_message_text(
        "🔍 Anime nomini yozing:\n\n"
        "(Masalan: Naruto, One Piece, ...)",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="main_menu")]])
    )

async def search_by_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    SEARCH_MODE[query.from_user.id] = 'code'
    await query.edit_message_text(
        "🔢 Anime kodini yozing:\n\n"
        "(Masalan: <code>AB12CD</code>)",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="main_menu")]])
    )

async def handle_search_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # Foydalanuvchi ro'yxatdan o'tganligini tekshirish
    from database.db import get_user as _get_user
    db_user = _get_user(user_id)
    if not db_user or not db_user.get('phone'):
        return  # start handler handles this

    mode = SEARCH_MODE.get(user_id, 'name')
    results = search_animes(text)

    if not results:
        await update.message.reply_text(
            "😕 Anime topilmadi!\n\nBoshqa nom/kod bilan urinib ko'ring.",
            reply_markup=back_button("main_menu")
        )
        return

    buttons = []
    for a in results[:15]:
        icon = "⭐" if a['is_premium'] else "🎌"
        buttons.append([InlineKeyboardButton(
            f"{icon} {a['name']} [{a['code']}]",
            callback_data=f"anime_{a['id']}"
        )])
    buttons.append([InlineKeyboardButton("🔙 Bosh menyu", callback_data="main_menu")])

    await update.message.reply_text(
        f"🔍 <b>Natijalar:</b> {len(results)} ta topildi",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def show_premium_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    animes = get_premium_animes()
    if not animes:
        await query.edit_message_text("⭐ Hozircha premium animelar yo'q.", reply_markup=back_button())
        return

    buttons = []
    for a in animes:
        buttons.append([InlineKeyboardButton(f"⭐ {a['name']} [{a['code']}]", callback_data=f"anime_{a['id']}")])
    buttons.append([InlineKeyboardButton("🔙 Bosh menyu", callback_data="main_menu")])

    await query.edit_message_text(
        f"⭐ <b>Premium Animelar</b> ({len(animes)} ta)",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def show_anime_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    anime_id = int(query.data.split('_')[1])
    anime = get_anime_by_id(anime_id)
    if not anime:
        await query.answer("Anime topilmadi!", show_alert=True)
        return

    episodes = get_episodes(anime_id)
    user_premium = is_premium(user_id)

    # Premium anime va premium bo'lmagan user
    if anime['is_premium'] and not user_premium:
        text = (
            f"⭐ <b>{anime['name']}</b>\n\n"
            f"{anime['description']}\n\n"
            f"🔒 <b>Bu anime PREMIUM!</b>\n\n"
            f"Premium olish uchun:\n👉 {PREMIUM_CONTACT} ga murojaat qiling"
        )
        buttons = [[InlineKeyboardButton("🔙 Orqaga", callback_data="premium_list")]]
        if anime.get('photo_id'):
            await query.message.reply_photo(
                photo=anime['photo_id'],
                caption=text,
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            await query.message.delete()
        else:
            await query.edit_message_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(buttons))
        return

    # Qismlar ro'yxati
    ep_buttons = []
    for ep in episodes:
        ep_buttons.append([InlineKeyboardButton(
            f"▶️ {ep['episode_number']}-qism: {ep['title']}",
            callback_data=f"ep_{anime_id}_{ep['episode_number']}"
        )])

    if not ep_buttons:
        ep_buttons.append([InlineKeyboardButton("⏳ Qismlar hali yuklanmagan", callback_data="noop")])

    # Manager/admin tugmasi
    db_user = get_user(user_id)
    if db_user and db_user['role'] in ('admin', 'manager'):
        ep_buttons.append([InlineKeyboardButton("➕ Qism qo'shish", callback_data=f"add_episode_{anime_id}")])

    ep_buttons.append([InlineKeyboardButton("🔙 Orqaga", callback_data="main_menu")])

    premium_badge = "⭐ PREMIUM • " if anime['is_premium'] else ""
    text = (
        f"🎌 <b>{anime['name']}</b>\n"
        f"🔢 Kod: <code>{anime['code']}</code> • {premium_badge}{len(episodes)} ta qism\n\n"
        f"{anime['description']}"
    )

    if anime.get('photo_id'):
        await query.message.reply_photo(
            photo=anime['photo_id'],
            caption=text,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(ep_buttons)
        )
        await query.message.delete()
    else:
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(ep_buttons))

async def show_episode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    parts = query.data.split('_')
    anime_id = int(parts[1])
    ep_num = int(parts[2])

    anime = get_anime_by_id(anime_id)
    ep = get_episode(anime_id, ep_num)

    if not ep:
        await query.answer("Qism topilmadi!", show_alert=True)
        return

    if anime['is_premium'] and not is_premium(user_id):
        await query.answer("⭐ Bu premium anime! Premium oling.", show_alert=True)
        return

    from utils import format_size
    caption = (
        f"🎬 <b>{anime['name']}</b>\n"
        f"📺 {ep['episode_number']}-qism: {ep['title']}\n"
        f"💾 Hajm: {format_size(ep.get('file_size') or 0)}"
    )

    await context.bot.send_video(
        chat_id=query.message.chat_id,
        video=ep['file_id'],
        caption=caption,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Anime sahifasi", callback_data=f"anime_{anime_id}")
        ]])
    )

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    from database.db import get_user
    db_user = get_user(query.from_user.id)
    if not db_user:
        return
    from handlers.start import show_main_menu
    await show_main_menu(update, context, db_user)
