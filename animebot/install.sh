#!/bin/bash
# Anime Bot - O'rnatish skripti
# ISPmanager/VPS da ishlatish uchun

echo "========================================"
echo "   🎌 Anime Bot - O'rnatish"
echo "========================================"

# Python tekshirish
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 topilmadi. O'rnatilmoqda..."
    apt-get update && apt-get install -y python3 python3-pip
fi

# Papka yaratish
BOT_DIR="/home/animebot"
echo "📁 Papka yaratilmoqda: $BOT_DIR"
mkdir -p $BOT_DIR
mkdir -p $BOT_DIR/uploads/anime
mkdir -p $BOT_DIR/database

# Fayllarni ko'chirish
echo "📋 Fayllar ko'chirilmoqda..."
cp -r ./* $BOT_DIR/
cp .env.example $BOT_DIR/.env

# Huquqlar
chmod 755 $BOT_DIR
chmod 777 $BOT_DIR/uploads
chmod 777 $BOT_DIR/uploads/anime

# Dependencies
echo "📦 Kutubxonalar o'rnatilmoqda..."
pip3 install -r $BOT_DIR/requirements.txt

echo ""
echo "========================================"
echo "✅ O'rnatish tugadi!"
echo ""
echo "KEYINGI QADAMLAR:"
echo "1. nano $BOT_DIR/.env    (token va ID kiriting)"
echo "2. sudo cp animebot.service /etc/systemd/system/"
echo "3. sudo systemctl enable animebot"
echo "4. sudo systemctl start animebot"
echo "5. sudo systemctl status animebot"
echo "========================================"
