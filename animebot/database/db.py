#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'anime_bot.db')

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        telegram_id INTEGER UNIQUE NOT NULL,
        username TEXT,
        full_name TEXT,
        phone TEXT,
        role TEXT DEFAULT 'user',
        premium_until DATETIME,
        joined_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # Animes table
    c.execute('''CREATE TABLE IF NOT EXISTS animes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT UNIQUE NOT NULL,
        description TEXT,
        photo_id TEXT,
        is_premium INTEGER DEFAULT 0,
        added_by INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # Episodes table
    c.execute('''CREATE TABLE IF NOT EXISTS episodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        anime_id INTEGER NOT NULL,
        episode_number INTEGER NOT NULL,
        title TEXT,
        file_id TEXT NOT NULL,
        file_size INTEGER DEFAULT 0,
        added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (anime_id) REFERENCES animes(id)
    )''')

    # Required channels
    c.execute('''CREATE TABLE IF NOT EXISTS channels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel_id TEXT UNIQUE NOT NULL,
        channel_name TEXT,
        is_premium_channel INTEGER DEFAULT 0,
        added_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()
    conn.close()
    print("✅ Database tayyor!")

# ─── USER FUNCTIONS ───────────────────────────────────────

def get_user(telegram_id):
    conn = get_conn()
    user = conn.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(telegram_id, username, full_name, phone=None):
    conn = get_conn()
    conn.execute(
        'INSERT OR IGNORE INTO users (telegram_id, username, full_name, phone) VALUES (?,?,?,?)',
        (telegram_id, username, full_name, phone)
    )
    conn.commit()
    conn.close()

def update_user_phone(telegram_id, phone):
    conn = get_conn()
    conn.execute('UPDATE users SET phone=? WHERE telegram_id=?', (phone, telegram_id))
    conn.commit()
    conn.close()

def set_user_role(telegram_id, role):
    conn = get_conn()
    conn.execute('UPDATE users SET role=? WHERE telegram_id=?', (role, telegram_id))
    conn.commit()
    conn.close()

def give_user_premium(telegram_id, days=30):
    conn = get_conn()
    until = datetime.now() + timedelta(days=days)
    conn.execute('UPDATE users SET premium_until=? WHERE telegram_id=?', (until.isoformat(), telegram_id))
    conn.commit()
    conn.close()
    return until

def is_premium(telegram_id):
    user = get_user(telegram_id)
    if not user:
        return False
    if user['role'] in ('admin', 'manager'):
        return True
    if user['premium_until']:
        return datetime.fromisoformat(user['premium_until']) > datetime.now()
    return False

def get_all_users(limit=50, offset=0):
    conn = get_conn()
    users = conn.execute('SELECT * FROM users ORDER BY joined_at DESC LIMIT ? OFFSET ?', (limit, offset)).fetchall()
    count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    conn.close()
    return [dict(u) for u in users], count

# ─── ANIME FUNCTIONS ──────────────────────────────────────

def add_anime(name, description, photo_id, is_premium, added_by):
    import random, string
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    conn = get_conn()
    conn.execute(
        'INSERT INTO animes (name, code, description, photo_id, is_premium, added_by) VALUES (?,?,?,?,?,?)',
        (name, code, description, photo_id, 1 if is_premium else 0, added_by)
    )
    conn.commit()
    anime_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    conn.close()
    return anime_id, code

def get_anime_by_id(anime_id):
    conn = get_conn()
    a = conn.execute('SELECT * FROM animes WHERE id=?', (anime_id,)).fetchone()
    conn.close()
    return dict(a) if a else None

def get_anime_by_code(code):
    conn = get_conn()
    a = conn.execute('SELECT * FROM animes WHERE code=?', (code.upper(),)).fetchone()
    conn.close()
    return dict(a) if a else None

def search_animes(query):
    conn = get_conn()
    results = conn.execute(
        'SELECT * FROM animes WHERE name LIKE ? OR code LIKE ? ORDER BY name',
        (f'%{query}%', f'%{query.upper()}%')
    ).fetchall()
    conn.close()
    return [dict(r) for r in results]

def get_premium_animes():
    conn = get_conn()
    results = conn.execute('SELECT * FROM animes WHERE is_premium=1 ORDER BY name').fetchall()
    conn.close()
    return [dict(r) for r in results]

def get_all_animes():
    conn = get_conn()
    results = conn.execute('SELECT * FROM animes ORDER BY name').fetchall()
    conn.close()
    return [dict(r) for r in results]

# ─── EPISODE FUNCTIONS ────────────────────────────────────

def add_episode(anime_id, episode_number, title, file_id, file_size=0):
    conn = get_conn()
    conn.execute(
        'INSERT INTO episodes (anime_id, episode_number, title, file_id, file_size) VALUES (?,?,?,?,?)',
        (anime_id, episode_number, title, file_id, file_size)
    )
    conn.commit()
    conn.close()

def get_episodes(anime_id):
    conn = get_conn()
    eps = conn.execute('SELECT * FROM episodes WHERE anime_id=? ORDER BY episode_number', (anime_id,)).fetchall()
    conn.close()
    return [dict(e) for e in eps]

def get_episode(anime_id, ep_number):
    conn = get_conn()
    ep = conn.execute('SELECT * FROM episodes WHERE anime_id=? AND episode_number=?', (anime_id, ep_number)).fetchone()
    conn.close()
    return dict(ep) if ep else None

# ─── CHANNEL FUNCTIONS ────────────────────────────────────

def get_channels():
    conn = get_conn()
    channels = conn.execute('SELECT * FROM channels').fetchall()
    conn.close()
    return [dict(c) for c in channels]

def add_channel(channel_id, channel_name, is_premium=0):
    conn = get_conn()
    conn.execute('INSERT OR IGNORE INTO channels (channel_id, channel_name, is_premium_channel) VALUES (?,?,?)',
                 (channel_id, channel_name, is_premium))
    conn.commit()
    conn.close()

def remove_channel(channel_id):
    conn = get_conn()
    conn.execute('DELETE FROM channels WHERE channel_id=?', (channel_id,))
    conn.commit()
    conn.close()
