# pages/show.py

import dash
from dash import html, dcc, callback, Input, Output
import sqlite3
import os

dash.register_page(__name__, path="/show", name="🛢️ SHOW - État de la base de données")

DB_PATH = "db/scraper_data.db"
CONFIG_DIR = "config"

def lire_table(table, limit=10):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table} ORDER BY rowid DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return html.Div(f"Aucune donnée dans {table}.", style={"color": "gray"})

    colonnes = rows[0].keys()

    en_tete = html.Tr([html.Th(c) for c in colonnes])
    lignes = []

    for row in rows:
        ligne = []
        for col in colonnes:
            valeur = str(row[col])
            if col == "texte":
                courte = (valeur[:50] + "…") if len(valeur) > 50 else valeur
                cellule = html.Td(courte, title=valeur)
            else:
                cellule = html.Td(valeur)
            ligne.append(cellule)
        lignes.append(html.Tr(ligne))

    return html.Table([html.Thead(en_tete), html.Tbody(lignes)],
                      style={"borderCollapse": "collapse", "width": "100%", "marginBottom": "10px"})

def lire_fichier(chemin):
    try:
        with open(chemin, "r", encoding="utf-8") as f:
            contenu = f.read()
        lignes = contenu.strip().splitlines()
        return html.Div([
            html.H4(f"📄 {os.path.basename(chemin)}"),
            html.Pre("\n".join(lignes), style={"backgroundColor": "#f9f9f9", "padding": "10px"})
        ])
    except Exception as e:
        return html.Div(f"Erreur lecture {chemin} : {e}", style={"color": "red"})

layout = html.Div([
    html.H2("🛢 État de la base de données et des fichiers"),

    dcc.Interval(
        id="show-rafraichissement",
        interval=30 * 1000,
        n_intervals=0
    ),

    html.Div(id="show-contenu")
])

@callback(
    Output("show-contenu", "children"),
    Input("show-rafraichissement", "n_intervals")
)
def rafraichir(n):
    contenu = []

    tables = ["CONTENU_RECUPERE", "PAGES_A_VISITER", "PAGE_VISITEE", "SITES_A_VISITER", "MOTS_CLES"]
    for nom in tables:
        contenu.append(html.H4(f"📄 Table {nom} (10 dernières entrées)"))
        contenu.append(lire_table(nom, limit=10))
        contenu.append(html.Hr())

    fichiers = ["keywords.txt", "url.txt", "conf.txt"]
    for nom in fichiers:
        chemin = os.path.join(CONFIG_DIR, nom)
        contenu.append(lire_fichier(chemin))
        contenu.append(html.Hr())

    return contenu
