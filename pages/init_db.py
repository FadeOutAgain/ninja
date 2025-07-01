# init_db.py : Crée ou réinitialise la base scraper_data.db avec les bonnes colonnes

import sqlite3
import os

DB_PATH = "db/scraper_data.db"

if os.path.exists(DB_PATH):
    print(f"🗑️ Suppression de l'ancienne base : {DB_PATH}")
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Création des tables
cur.execute("""
CREATE TABLE IF NOT EXISTS MOTS_CLES (
    mot TEXT PRIMARY KEY
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS SITES_A_VISITER (
    url TEXT PRIMARY KEY
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS PAGES_A_VISITER (
    url TEXT PRIMARY KEY,
    profondeur INTEGER,
    date_visite TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS CONTENU_RECUPERE (
    date TEXT,
    mots_cles TEXT,
    titre TEXT,
    texte TEXT,
    site TEXT,
    url TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS PAGE_VISITEE (
    url TEXT PRIMARY KEY,
    profondeur INTEGER,
    date_visite TEXT
)
""")

conn.commit()
conn.close()
print("✅ Base de données créée avec succès :", DB_PATH)
