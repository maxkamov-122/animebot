# 🎌 Anime Telegram Bot — To'liq Qo'llanma

## 📁 Fayl Tuzilmasi

```
animebot/
├── bot.py                  ← Asosiy bot fayli (ishga tushirish)
├── config.py               ← Sozlamalar (token, admin ID, limitlar)
├── utils.py                ← Yordamchi funksiyalar
├── requirements.txt        ← Kerakli kutubxonalar
├── animebot.service        ← systemd xizmati (24/7 uchun)
├── install.sh              ← O'rnatish skripti
├── .env.example            ← Muhit o'zgaruvchilari namunasi
├── database/
│   ├── __init__.py
│   └── db.py               ← SQLite ma'lumotlar bazasi
├── handlers/
│   ├── __init__.py
│   ├── start.py            ← Boshlash, ro'yxatdan o'tish
│   ├── admin.py            ← Admin panel
│   ├── manager.py          ← Anime/qism qo'shish
│   ├── anime.py            ← Izlash, ko'rish
│   └── user.py             ← Profil
└── uploads/
    └── anime/              ← (ixtiyoriy local saqlash)
```

---

## 🚀 ISPmanager Orqali O'rnatish

### 1-qadam: VPS serverga kirish

ISPmanager → **Server** → **Terminal** yoki SSH orqali:
```bash
ssh root@SERVER_IP
```

### 2-qadam: Python va pip o'rnatish

```bash
apt-get update
apt-get install -y python3 python3-pip
python3 --version   # 3.8+ bo'lishi kerak
```

### 3-qadam: Bot fayllarini yuklash

**FTP orqali:**
- ISPmanager → File Manager → `/home/animebot/` papka yarating
- Barcha fayllarni shu papkaga yuklang

**yoki SCP orqali:**
```bash
scp -r ./animebot/ root@SERVER_IP:/home/animebot/
```

### 4-qadam: Kutubxonalarni o'rnatish

```bash
cd /home/animebot
pip3 install -r requirements.txt
```

### 5-qadam: .env faylni sozlash

```bash
cp .env.example .env
nano .env
```

`.env` ichiga:
```env
BOT_TOKEN=1234567890:ABCDefGHIjklMNOpqrSTUVwxyz
ADMIN_IDS=123456789
PREMIUM_CONTACT=@your_username
```

**Bot token olish:** [@BotFather](https://t.me/BotFather) → `/newbot`

**O'z Telegram ID-ingizni bilish:** [@userinfobot](https://t.me/userinfobot) ga `/start` yuboring

### 6-qadam: Botni sinash

```bash
cd /home/animebot
python3 bot.py
```

Agar xato yo'q bo'lsa: `✅ Database tayyor!` va `Bot ishga tushdi!` chiqadi.

---

## ⚙️ 24/7 Ishlash Uchun systemd

### Sozlash:

```bash
# Servis faylni ko'chirish
cp /home/animebot/animebot.service /etc/systemd/system/

# Yoqish
systemctl daemon-reload
systemctl enable animebot
systemctl start animebot

# Holatini tekshirish
systemctl status animebot
```

### Boshqarish:

```bash
systemctl stop animebot      # To'xtatish
systemctl restart animebot   # Qayta ishga tushirish
journalctl -u animebot -f    # Loglarni ko'rish (real-time)
```

---

## 🗄️ phpMyAdmin Haqida

Bu bot **SQLite** ishlatadi — alohida MySQL server kerak emas!

**Ma'lumotlar bazasi:** `/home/animebot/anime_bot.db`

Agar siz phpMyAdmin ishlatmoqchi bo'lsangiz, DB ni MySQL'ga o'tkazish mumkin, lekin SQLite yetarli va sodda.

**SQLite faylni ochish:**
```bash
sqlite3 /home/animebot/anime_bot.db
.tables          # jadvallarni ko'rish
SELECT * FROM users;
.quit
```

---

## 🎌 Bot Funksiyalari

### 👤 Oddiy foydalanuvchi:
- `/start` → profil yuborish → bosh menyu
- Anime izlash (nom yoki kod bilan)
- Premium animelar ro'yxatini ko'rish
- Bepul animeni ko'rish
- Premium anime → "Premium oling" deb ko'rsatadi
- O'z profilini ko'rish

### 🔑 Manager:
- Yuqoridagilarning hammasi
- Yangi anime qo'shish (nom, rasm, tavsif, premium/bepul)
- Anime qismlarini yuklash (video, 2GB gacha)

### 👑 Admin:
- Yuqoridagilarning hammasi
- Barcha foydalanuvchilarni ko'rish
- User → Manager yoki User qilish
- Foydalanuvchiga premium berish (30 kun)
- Majburiy obuna kanallarini boshqarish (qo'shish/o'chirish)

---

## 📺 Video Fayl Hajmi

- **Maksimal:** 2 GB (1 ta qism uchun)
- **Saqlash:** Telegram serverlari (file_id sifatida)
- **Server disk:** Faqat ma'lumotlar bazasi (.db fayl) saqlanadi
- Telegram o'zi videolarni 20 yilgacha saqlaydi

---

## 📢 Majburiy Obuna Qo'shish

1. Botni kanalingizga **admin** qiling
2. Admin panelida → **Kanallar boshqaruvi** → **Kanal qo'shish**
3. Kanal ID kiriting: `@kanalingiz` yoki `-1001234567890`

---

## 🔧 Muammolarni Hal Qilish

| Muammo | Yechim |
|--------|--------|
| `ModuleNotFoundError` | `pip3 install -r requirements.txt` |
| Bot javob bermayapti | `systemctl status animebot` → xatolarni ko'ring |
| Video yuklanmayapti | Bot @BotFather da `large files` limitini tekshiring |
| Kanal tekshiruvi ishlamayapti | Bot kanalga admin bo'lishi kerak |
| ID topilmadi | [@userinfobot](https://t.me/userinfobot) ga `/start` yuboring |

---

## 💡 Muhim Eslatmalar

1. **Token** hech kimga bermang
2. `.env` faylni serverda saqlang, GitHubga yuklash
3. Har kuni `journalctl -u animebot` orqali loglarni kuzating
4. Server diskida kamida **10 GB** bo'sh joy bo'lsin (DB o'sishi uchun)
