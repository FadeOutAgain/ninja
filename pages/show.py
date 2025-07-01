# pages/show.py

import dash
from dash import html
import sqlite3
import os

dash.register_page(__name__, path="/show", name="👁️ Show")

# Chargement de la configuration
def charger_config(path='config/conf.txt'):
    config = {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for ligne in f:
                if '=' in ligne:
                    cle, val = ligne.strip().split('=', 1)
                    config[cle.strip()] = val.strip()
    except Exception:
        pass
    config.setdefault('db_path', 'db/scraper_data.db')
    return config

config = charger_config()
db_path = config['db_path']

def compter_lignes(table):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        result = cur.fetchone()[0]
        conn.close()
        return result
    except Exception as e:
        return f"Erreur ({table}) : {e}"

def lire_fichier(path, max_lines=40):
    if not os.path.exists(path):
        return f"Fichier introuvable : {path}"
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lignes = f.readlines()
        return ''.join(lignes[-max_lines:])

def lire_derniers_enregistrements(table, colonnes, limit=10):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(f"SELECT {', '.join(colonnes)} FROM {table} ORDER BY ROWID DESC LIMIT ?", (limit,))
        lignes = cur.fetchall()
        conn.close()
        return '\n'.join([str(dict(zip(colonnes, ligne))) for ligne in lignes])
    except Exception as e:
        return f"Erreur de lecture : {e}"

layout = html.Div([
    html.H3("📂 Informations sur la base de données"),

    html.Ul([
        html.Li(f"MOTS_CLES : {compter_lignes('MOTS_CLES')} entrée(s)"),
        html.Li(f"SITES_A_VISITER : {compter_lignes('SITES_A_VISITER')} site(s)"),
        html.Li(f"PAGES_A_VISITER : {compter_lignes('PAGES_A_VISITER')} page(s)"),
        html.Li(f"PAGE_VISITEE : {compter_lignes('PAGE_VISITEE')} page(s)"),
        html.Li(f"CONTENU_RECUPERE : {compter_lignes('CONTENU_RECUPERE')} contenu(s)"),
    ]),

    html.Hr(),

    html.H4("📄 Fichier de configuration"),
    html.Pre(lire_fichier('config/conf.txt'), style={"backgroundColor": "#f9f9f9"}),

    html.H4("🔑 Mots-clés (keywords.txt)"),
    html.Pre(lire_fichier('config/keywords.txt'), style={"backgroundColor": "#f9f9f9"}),

    html.H4("🌐 URLs à visiter (url.txt)"),
    html.Pre(lire_fichier('config/url.txt'), style={"backgroundColor": "#f9f9f9"}),

    html.Hr(),

    html.H4("🧾 10 dernières entrées — MOTS_CLES"),
    html.Pre(lire_derniers_enregistrements('MOTS_CLES', ['mot']), style={"backgroundColor": "#f0f0f0"}),

    html.H4("🧾 10 dernières entrées — SITES_A_VISITER"),
    html.Pre(lire_derniers_enregistrements('SITES_A_VISITER', ['url']), style={"backgroundColor": "#f0f0f0"}),

    html.H4("🧾 10 dernières entrées — PAGES_A_VISITER"),
    html.Pre(lire_derniers_enregistrements('PAGES_A_VISITER', ['url', 'profondeur', 'date_visite']), style={"backgroundColor": "#f0f0f0"}),

    html.H4("🧾 10 dernières entrées — PAGE_VISITEE"),
    html.Pre(lire_derniers_enregistrements('PAGE_VISITEE', ['url', 'date_visite']), style={"backgroundColor": "#f0f0f0"}),

    html.H4("🧾 10 dernières entrées — CONTENU_RECUPERE"),
    html.Pre(lire_derniers_enregistrements('CONTENU_RECUPERE', ['date', 'mots_cles', 'titre', 'site']), style={"backgroundColor": "#f0f0f0"})
])
