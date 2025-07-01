import sqlite3
import os

DB_PATH = "db/scraper_data.db"

os.makedirs("db", exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Table des mots-clés à surveiller
cur.execute("""
CREATE TABLE IF NOT EXISTS MOTS_CLES (
    mot TEXT PRIMARY KEY
)
""")

# Table des sites de départ
cur.execute("""
CREATE TABLE IF NOT EXISTS SITES_A_VISITER (
    url TEXT PRIMARY KEY
)
""")

# Table des pages à visiter
cur.execute("""
CREATE TABLE IF NOT EXISTS PAGES_A_VISITER (
    url TEXT PRIMARY KEY,
    profondeur INTEGER,
    date_visite TEXT
)
""")

# Table des pages déjà visitées (historique)
cur.execute("""
CREATE TABLE IF NOT EXISTS PAGE_VISITEE (
    url TEXT,
    profondeur INTEGER,
    date_visite TEXT,
    PRIMARY KEY (url, date_visite)
)
""")

# Table des contenus pertinents détectés
cur.execute("""
CREATE TABLE IF NOT EXISTS CONTENU_RECUPERE (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    mots_cles TEXT,
    titre TEXT,
    texte TEXT,
    site TEXT,
    url TEXT
)
""")

# Index composite pour éviter les doublons texte + url
cur.execute("""
CREATE INDEX IF NOT EXISTS idx_url_texte ON CONTENU_RECUPERE (url, texte)
""")

# Index utiles pour rapidité des requêtes (facultatif)
cur.execute("""
CREATE INDEX IF NOT EXISTS idx_date_visite ON PAGES_A_VISITER (date_visite)
""")

cur.execute("""
CREATE INDEX IF NOT EXISTS idx_page_url_date ON PAGE_VISITEE (url, date_visite)
""")

conn.commit()
conn.close()

print(f"✅ Base de données initialisée : {DB_PATH}")
