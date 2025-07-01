# common.py : Fonctions communes utilisées par NINJA et APP

import os
import sqlite3
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import pandas as pd

# Chargement de la configuration depuis le fichier config/conf.txt
def charger_config():
    config = {}
    try:
        with open(os.path.join("config", "conf.txt"), "r", encoding="utf-8") as f:
            for line in f:
                if '=' in line:
                    k, v = line.strip().split('=', 1)
                    config[k.strip()] = v.strip()
    except Exception as e:
        print(f"[ERREUR] Impossible de lire la configuration : {e}")
    return config

# Lecture simplifiée de la configuration pour l'application APP.py (équivalent de charger_config)
def lire_conf():
    return charger_config()

# Récupère le chemin de la base de données depuis la conf
def get_db_path():
    config = charger_config()
    return config.get("db_path", "db/scraper_data.db")

# Connexion SQLite avec chemin dynamique
def get_connexion(db_path):
    return sqlite3.connect(db_path, check_same_thread=False)

# Fonction pour lire une table SQL avec pandas
def lire_table(query, db_path=None, params=()):
    if db_path is None:
        db_path = get_db_path()
    try:
        conn = get_connexion(db_path)
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        print(f"[ERREUR] Lecture de table échouée : {e}")
        return pd.DataFrame()

# Taille lisible de la base
def get_db_size(db_path):
    try:
        taille = os.path.getsize(db_path) / 1024
        return f"{taille:.1f} Ko"
    except:
        return "0 Ko"

# Nombre de mots clés dans la base
def get_nb_keywords(db_path):
    try:
        conn = get_connexion(db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM MOTS_CLES")
        nb = cur.fetchone()[0]
        conn.close()
        return nb
    except:
        return 0

# Nombre de sites dans la base
def get_nb_sites(db_path):
    try:
        conn = get_connexion(db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM SITES_A_VISITER")
        nb = cur.fetchone()[0]
        conn.close()
        return nb
    except:
        return 0

# Journalisation dans le fichier log défini dans la config
def log(message, log_file="logs/ninja.log"):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} {message}\n")
        print(f"{timestamp} {message}")
    except:
        print(f"[ERREUR] Impossible d'écrire dans le fichier de log : {log_file}")

# Nettoyage de texte brut HTML
def nettoyer_texte(texte):
    return ' '.join(texte.strip().split())

# Extraction de liens internes HTML filtrés
def extraire_liens(html, base_url):
    try:
        soup = BeautifulSoup(html, "html.parser")
        liens = set()
        domaine = urlparse(base_url).netloc
        for a in soup.find_all("a", href=True):
            href = a['href']
            url = urljoin(base_url, href)
            if urlparse(url).netloc == domaine:
                if not any(url.lower().endswith(ext) for ext in [".jpg", ".png", ".gif", ".pdf", ".zip", ".doc", ".exe", ".mp4"]):
                    liens.add(url)
        return list(liens)
    except:
        return []

# Lecture des mots-clés depuis keywords.txt
def lire_keywords():
    try:
        with open("config/keywords.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

# Lecture des URLs depuis url.txt
def lire_urls():
    try:
        with open("config/url.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []
