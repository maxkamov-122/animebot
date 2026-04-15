#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

# ─── BOT SOZLAMALARI ──────────────────────────────────────
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Admin Telegram ID (sening ID-ing)
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '123456789').split(',')]

# Premium kontakt (admin yoki manager username)
PREMIUM_CONTACT = "@your_admin_username"

# Video fayl maksimal hajmi (bytes) — 2GB
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB

# Majburiy obuna kanalidagi tekshirish
CHECK_SUBSCRIPTION = True

# Premium muddat (kunlarda)
PREMIUM_DAYS = 30

# Upload papkasi
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'anime')
