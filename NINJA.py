import sqlite3
import os
import time
import random
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from colorama import Fore, Style, init
init(autoreset=True)  # pour réinitialiser automatiquement les couleurs

import requests
from datetime import datetime

def charger_config(path="config/conf.txt"):
    config = {
        "db_path": "db/scraper_data.db",
        "delay": 1000,
        "max_depth": 2,
        "expiration": 30,
        "log_file": "log.txt"
    }
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for ligne in f:
                if "=" in ligne:
                    cle, val = ligne.strip().split("=", 1)
                    config[cle.strip()] = val.strip()
    config["delay"] = int(config.get("delay", 1000))
    config["max_depth"] = int(config.get("max_depth", 2))
    config["expiration"] = int(config.get("expiration", 30))
    return config

def log(msg, path):
    horodatage = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{horodatage} {msg}"
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(Fore.LIGHTGREEN_EX + line)

def charger_liste(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip()]

def nettoyer_texte(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)

def extraire_liens(base_url, html):
    soup = BeautifulSoup(html, "html.parser")
    liens = set()
    for a in soup.find_all("a", href=True):
        href = urljoin(base_url, a["href"])
        if href.startswith("http"):
            href = href.split("#")[0]
            liens.add(href)
    return list(liens)

def domaine(url):
    return urlparse(url).netloc

# === Initialisation ===
config = charger_config()
log_file = config["log_file"]
db_path = config["db_path"]

log("------- 🏁 Démarrage de Ninja -------", log_file)
conn = sqlite3.connect(db_path)
cur = conn.cursor()
log(f"Connexion à la base : {db_path}", log_file)

# Chargement des mots-clés
mots_cles = charger_liste("config/keywords.txt")
cur.execute("DELETE FROM MOTS_CLES")
for mot in mots_cles:
    cur.execute("INSERT OR IGNORE INTO MOTS_CLES (mot) VALUES (?)", (mot,))
conn.commit()
log(f"{len(mots_cles)} mot(s)-clé(s) chargé(s)", log_file)

# Chargement des sites
sites = charger_liste("config/url.txt")
cur.execute("DELETE FROM SITES_A_VISITER")
for site in sites:
    cur.execute("INSERT OR IGNORE INTO SITES_A_VISITER (url) VALUES (?)", (site,))
conn.commit()
log(f"{len(sites)} site(s) à visiter chargé(s)", log_file)

# Insertion ou réactivation dans PAGES_A_VISITER
for url in sites:
    cur.execute("""
        INSERT OR IGNORE INTO PAGES_A_VISITER (url, profondeur, date_visite)
        VALUES (?, 0, NULL)
    """, (url,))
    cur.execute("""
        UPDATE PAGES_A_VISITER SET date_visite = NULL, profondeur = 0
        WHERE url = ?
    """, (url,))
conn.commit()

# Suppression des PAGES_A_VISITER hors SITES_A_VISITER

cur.execute("SELECT url FROM PAGES_A_VISITER")
pages = cur.fetchall()

urls_a_supprimer = [
    (url,) for (url,) in pages
    if not any(url.startswith(site) for site in sites)
]

if urls_a_supprimer:
    cur.executemany("DELETE FROM PAGES_A_VISITER WHERE url = ?", urls_a_supprimer)
    log(f"🧹 {len(urls_a_supprimer)} URL supprimée(s) de PAGES_A_VISITER (hors domaine)", log_file)
else:
    log("🧹 Aucune URL hors domaine à supprimer dans PAGES_A_VISITER", log_file)

conn.commit()



# Nettoyage : suppression des contenus récupérés hors domaine
cur.execute("SELECT url FROM CONTENU_RECUPERE")
contenus = cur.fetchall()

urls_contenus_a_supprimer = [
    (url,) for (url,) in contenus
    if not any(url.startswith(site) for site in sites)
]

if urls_contenus_a_supprimer:
    cur.executemany("DELETE FROM CONTENU_RECUPERE WHERE url = ?", urls_contenus_a_supprimer)
    log(f"🧹 {len(urls_contenus_a_supprimer)} contenu(s) supprimé(s) de CONTENU_RECUPERE (hors domaine)", log_file)
else:
    log("🧹 Aucun contenu hors domaine à supprimer dans CONTENU_RECUPERE", log_file)

conn.commit()




# === Boucle d'exploration ===
expiration_minutes = config["expiration"]
delay_seconds = config["delay"] / 1000
max_depth = config["max_depth"]

while True:
    cur.execute("""
        SELECT url, profondeur FROM PAGES_A_VISITER
        WHERE date_visite IS NULL
    """)
    non_visitees = cur.fetchall()

    cur.execute("""
        SELECT url, profondeur FROM PAGES_A_VISITER
        WHERE date_visite IS NOT NULL
          AND datetime(date_visite) <= datetime('now', '-1 day')
        ORDER BY RANDOM()
    """)
    anciennes = cur.fetchall()
    lignes = non_visitees + anciennes

    log(f"📋 Pages à explorer : {len(non_visitees)} non visitées + {len(anciennes)} anciennes (>{config['expiration']} min)", log_file)

    
    if not lignes:
        log("🛑 Aucune page à visiter. Fin du scraping.", log_file)

        cur.execute("SELECT COUNT(*) FROM CONTENU_RECUPERE")
        contenus = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM PAGE_VISITEE")
        visitees = cur.fetchone()[0]
        log(f"🔚 Statistiques : {visitees} pages visitées – {contenus} contenus collectés", log_file)

        break

    for url, profondeur in lignes:
        maintenant = datetime.now()
        print(Fore.LIGHTCYAN_EX + f"🔍 Exploration : {url} (profondeur {profondeur})")

        try:
            response = requests.get(url, timeout=10)
            html = response.text
            texte = nettoyer_texte(html)

            horodatage = maintenant.strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("""
                UPDATE PAGES_A_VISITER SET date_visite = ? WHERE url = ?
            """, (horodatage, url))
            cur.execute("""
                INSERT OR IGNORE INTO PAGE_VISITEE (url, profondeur, date_visite)
                VALUES (?, ?, ?)
            """, (url, profondeur, horodatage))

            mots_trouves = [mot for mot in mots_cles if mot.lower() in texte.lower()]
            if mots_trouves:
                titre = BeautifulSoup(html, "html.parser").title
                titre = titre.text.strip() if titre else "(sans titre)"

                # Vérifie si ce contenu a déjà été enregistré (même URL, même texte)
                cur.execute("""
                    SELECT 1 FROM CONTENU_RECUPERE
                    WHERE url = ? AND texte = ?
                """, (url, texte[:1000]))
                existe_deja = cur.fetchone()

                # Et si ce n'est pas le cas, on ajoute dans CONTENU_RECUPERE 

                if not existe_deja:
                    cur.execute("""
                        INSERT INTO CONTENU_RECUPERE (date, mots_cles, titre, texte, site, url)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        horodatage,
                        ", ".join(mots_trouves),
                        titre,
                        texte[:1000],
                        domaine(url),
                        url
                    ))
                    detection_msg = f"⚠️  Mot(s)-clé détecté(s) : {', '.join(mots_trouves)} dans {titre}"
                    log(detection_msg, log_file)
                else:
                    log(f"🔁 Aucun ajout : contenu déjà connu pour {url}", log_file)

            # Ajouter nouveaux liens
            if profondeur < max_depth:
                for lien in extraire_liens(url, html):
                    if domaine(lien) != domaine(url):
                        continue
                    if "." in lien.split("/")[-1] and not lien.endswith(".html"):
                        continue
                    cur.execute("SELECT 1 FROM PAGES_A_VISITER WHERE url = ?", (lien,))
                    if not cur.fetchone():
                        cur.execute("""
                            INSERT INTO PAGES_A_VISITER (url, profondeur, date_visite)
                            VALUES (?, ?, NULL)
                        """, (lien, profondeur + 1))
                        print(Fore.CYAN + " Ajout d'une page à visiter :"+url)

            conn.commit()
            time.sleep(delay_seconds)

        except Exception as e:
            log(f"Erreur sur {url} : {e}", log_file)
            cur.execute("""
                UPDATE PAGES_A_VISITER SET date_visite = ? WHERE url = ?
            """, (maintenant.strftime("%Y-%m-%d %H:%M:%S"), url))
            cur.execute("""
                INSERT OR IGNORE INTO PAGE_VISITEE (url, profondeur, date_visite)
                VALUES (?, ?, ?)
            """, (url, profondeur, maintenant.strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            time.sleep(delay_seconds)
