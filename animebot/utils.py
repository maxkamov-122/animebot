#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from database.db import get_channels
from config import ADMIN_IDS

async def check_subscription(bot, user_id):
    """Foydalanuvchi barcha kanallarga obuna bo'lganini tekshiradi"""
    channels = get_channels()
    not_subscribed = []
    for ch in channels:
        try:
            member = await bot.get_chat_member(ch['channel_id'], user_id)
            if member.status in ('left', 'kicked', 'restricted'):
                not_subscribed.append(ch)
        except Exception:
            pass
    return not_subscribed

def main_menu_keyboard(role='user'):
    buttons = [
        [InlineKeyboardButton("🔍 Anime izlash (nom)", callback_data="search_name"),
         InlineKeyboardButton("🔢 Kod bilan izlash", callback_data="search_code")],
        [InlineKeyboardButton("⭐ Premium Animelar", callback_data="premium_list")],
        [InlineKeyboardButton("👤 Mening profilim", callback_data="my_profile")],
    ]
    if role in ('admin', 'manager'):
        buttons.append([InlineKeyboardButton("➕ Anime qo'shish", callback_data="add_anime")])
    if role == 'admin':
        buttons.append([InlineKeyboardButton("🔧 Admin Panel", callback_data="admin_panel_main")])
    return InlineKeyboardMarkup(buttons)

def subscription_keyboard(channels):
    buttons = []
    for ch in channels:
        name = ch.get('channel_name') or ch['channel_id']
        buttons.append([InlineKeyboardButton(f"📢 {name}", url=f"https://t.me/{ch['channel_id'].lstrip('@')}")])
    buttons.append([InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")])
    return InlineKeyboardMarkup(buttons)

def contact_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Profilimni yuborish", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )

def back_button(callback="main_menu"):
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data=callback)]])

def is_admin(user_id):
    return user_id in ADMIN_IDS

def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/1024**2:.1f} MB"
    else:
        return f"{size_bytes/1024**3:.2f} GB"
