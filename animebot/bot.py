#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters
)
from handlers import start, admin, manager, anime, user
from database.db import init_db

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    # Start & Registration
    app.add_handler(CommandHandler("start", start.start_command))
    app.add_handler(MessageHandler(filters.CONTACT, start.handle_contact))

    # Admin handlers
    app.add_handler(CommandHandler("admin", admin.admin_panel))
    app.add_handler(CallbackQueryHandler(admin.admin_users_list, pattern="^admin_users$"))
    app.add_handler(CallbackQueryHandler(admin.admin_user_detail, pattern="^admin_user_\\d+$"))
    app.add_handler(CallbackQueryHandler(admin.set_role, pattern="^set_role_"))
    app.add_handler(CallbackQueryHandler(admin.give_premium, pattern="^give_premium_\\d+$"))
    app.add_handler(CallbackQueryHandler(admin.manage_channels, pattern="^admin_channels$"))
    app.add_handler(CallbackQueryHandler(admin.add_channel_start, pattern="^add_channel$"))
    app.add_handler(CallbackQueryHandler(admin.remove_channel, pattern="^remove_channel_"))
    app.add_handler(CallbackQueryHandler(admin.back_to_admin, pattern="^back_admin$"))

    # Manager handlers
    app.add_handler(CallbackQueryHandler(manager.add_anime_start, pattern="^add_anime$"))
    app.add_handler(CallbackQueryHandler(manager.add_episode_start, pattern="^add_episode_\\d+$"))

    # Anime conversation (add anime)
    add_anime_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(manager.add_anime_start, pattern="^add_anime$")],
        states={
            manager.ANIME_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, manager.get_anime_name)],
            manager.ANIME_PHOTO: [MessageHandler(filters.PHOTO, manager.get_anime_photo)],
            manager.ANIME_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, manager.get_anime_desc)],
            manager.ANIME_PREMIUM: [CallbackQueryHandler(manager.get_anime_premium, pattern="^premium_(yes|no)$")],
        },
        fallbacks=[CommandHandler("cancel", manager.cancel)],
        allow_reentry=True
    )

    # Episode conversation
    add_episode_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(manager.add_episode_start, pattern="^add_episode_\\d+$")],
        states={
            manager.EP_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, manager.get_ep_number)],
            manager.EP_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, manager.get_ep_title)],
            manager.EP_VIDEO: [MessageHandler(filters.VIDEO | filters.Document.VIDEO, manager.get_ep_video)],
        },
        fallbacks=[CommandHandler("cancel", manager.cancel)],
        allow_reentry=True
    )

    # Add channel conversation
    add_channel_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin.add_channel_start, pattern="^add_channel$")],
        states={
            admin.CHANNEL_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin.save_channel)],
        },
        fallbacks=[CommandHandler("cancel", admin.cancel_admin)],
        allow_reentry=True
    )

    app.add_handler(add_anime_conv)
    app.add_handler(add_episode_conv)
    app.add_handler(add_channel_conv)

    # User search and navigation
    app.add_handler(CallbackQueryHandler(anime.search_by_name, pattern="^search_name$"))
    app.add_handler(CallbackQueryHandler(anime.search_by_code, pattern="^search_code$"))
    app.add_handler(CallbackQueryHandler(anime.show_premium_list, pattern="^premium_list$"))
    app.add_handler(CallbackQueryHandler(anime.show_anime_detail, pattern="^anime_\\d+$"))
    app.add_handler(CallbackQueryHandler(anime.show_episode, pattern="^ep_\\d+_\\d+$"))
    app.add_handler(CallbackQueryHandler(anime.back_to_main, pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(user.my_profile, pattern="^my_profile$"))

    # Text search
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anime.handle_search_text))

    logger.info("Bot ishga tushdi!")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
