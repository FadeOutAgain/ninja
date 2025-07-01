# pages/dash.py

import dash
from dash import html, dcc, callback, Input, Output, State
import sqlite3
import math
from datetime import datetime

dash.register_page(__name__, path="/dash", name="📁 DASH")

DB_PATH = "db/scraper_data.db"
LIMITE_PAR_PAGE = 20

def lire_contenus(filtre_site, filtre_mot, recherche_libre, page):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    where_clauses = []
    params = []

    if filtre_site:
        where_clauses.append("site = ?")
        params.append(filtre_site)

    if filtre_mot:
        where_clauses.append("mots_cles LIKE ?")
        params.append(f"%{filtre_mot}%")

    if recherche_libre:
        where_clauses.append("(titre LIKE ? OR texte LIKE ?)")
        params.extend([f"%{recherche_libre}%", f"%{recherche_libre}%"])

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    offset = (page - 1) * LIMITE_PAR_PAGE
    cur.execute(f"""
        SELECT date, mots_cles, titre, site, url
        FROM CONTENU_RECUPERE
        {where_sql}
        ORDER BY date DESC
        LIMIT ? OFFSET ?
    """, (*params, LIMITE_PAR_PAGE, offset))
    resultats = cur.fetchall()

    cur.execute(f"SELECT COUNT(*) FROM CONTENU_RECUPERE {where_sql}", params)
    total = cur.fetchone()[0]
    conn.close()
    return resultats, total

def lire_liste_sites():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT site FROM CONTENU_RECUPERE ORDER BY site ASC")
        sites = [row[0] for row in cur.fetchall()]
        conn.close()
        return sites
    except Exception:
        return []

def lire_liste_mots_cles():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT mots_cles FROM CONTENU_RECUPERE")
        tous = cur.fetchall()
        conn.close()

        mots_uniques = set()
        for row in tous:
            if row[0]:
                mots = [m.strip() for m in row[0].split(",") if m.strip()]
                mots_uniques.update(mots)
        return sorted(mots_uniques)
    except Exception:
        return []

def temps_ecoule(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        diff = datetime.now() - dt
        minutes = int(diff.total_seconds() // 60)
        heures, minutes = divmod(minutes, 60)
        return f"{heures}h {minutes}min"
    except Exception:
        return "?"

layout = html.Div([
    html.H3("📁 Contenus pertinents récupérés"),

    html.Div([
        html.Div([
            dcc.Dropdown(
                id="dash-filtre-site",
                options=[{"label": "Tous les sites", "value": ""}] + [
                    {"label": s, "value": s} for s in lire_liste_sites()
                ],
                value="",
                clearable=False
            )
        ], style={"width": "32%", "display": "inline-block", "marginRight": "2%"}),

        html.Div([
            dcc.Dropdown(
                id="dash-filtre-mot",
                options=[{"label": "Tous les mots-clés", "value": ""}] + [
                    {"label": m, "value": m} for m in lire_liste_mots_cles()
                ],
                value="",
                clearable=False
            )
        ], style={"width": "32%", "display": "inline-block", "marginRight": "2%"}),

        html.Div([
            dcc.Input(
                id="dash-recherche-libre",
                type="text",
                placeholder="Recherche libre...",
                debounce=True,
                style={"width": "100%"}
            )
        ], style={"width": "30%", "display": "inline-block"})
    ], style={"marginBottom": "20px"}),

    html.Div(id="dash-table-contenus"),
    html.Div(id="dash-pagination", style={"marginTop": "20px", "textAlign": "center"}),

    dcc.Store(id="dash-page-actuelle", data=1),

    # ✅ Déclaration invisible pour éviter les erreurs "nonexistent Input"
    html.Div([
        html.Button("⏮️", id="dash-prev", style={"display": "none"}),
        html.Button("⏭️", id="dash-next", style={"display": "none"})
    ], style={"display": "none"})
])

@callback(
    Output("dash-page-actuelle", "data"),
    Input("dash-prev", "n_clicks"),
    Input("dash-next", "n_clicks"),
    Input("dash-filtre-site", "value"),
    Input("dash-filtre-mot", "value"),
    Input("dash-recherche-libre", "value"),
    State("dash-page-actuelle", "data")
)
def mettre_a_jour_page(prev_clicks, next_clicks, site, mot, recherche, page_actuelle):
    ctx = dash.callback_context
    if not ctx.triggered:
        return page_actuelle

    declencheur = ctx.triggered[0]["prop_id"].split(".")[0]

    _, total = lire_contenus(site, mot, recherche, 1)
    max_page = max(1, math.ceil(total / LIMITE_PAR_PAGE))

    if declencheur == "dash-prev" and page_actuelle > 1:
        return page_actuelle - 1
    elif declencheur == "dash-next" and page_actuelle < max_page:
        return page_actuelle + 1
    elif declencheur in {"dash-filtre-site", "dash-filtre-mot", "dash-recherche-libre"}:
        return 1
    return page_actuelle

@callback(
    Output("dash-table-contenus", "children"),
    Output("dash-pagination", "children"),
    Input("dash-page-actuelle", "data"),
    State("dash-filtre-site", "value"),
    State("dash-filtre-mot", "value"),
    State("dash-recherche-libre", "value")
)
def afficher_contenus(page, site, mot, recherche):
    donnees, total = lire_contenus(site, mot, recherche, page)
    pages_totales = max(1, math.ceil(total / LIMITE_PAR_PAGE))

    lignes = []
    for date, mots, titre, site, url in donnees:
        lignes.append(html.Tr([
            html.Td(html.B(mots, style={"color": "red"})),
            html.Td(html.A(titre, href=url, target="_blank")),
            html.Td(site, style={"fontSize": "small", "color": "gray", "whiteSpace": "nowrap"}),
            html.Td(temps_ecoule(date), style={"fontSize": "small", "color": "#444", "whiteSpace": "nowrap"})
        ]))

    tableau = html.Table([
        html.Thead(html.Tr([
            html.Th("🔑 Mots-clés"),
            html.Th("📝 Titre"),
            html.Th("🌐 Site"),
            html.Th("⏱️ Depuis"),
        ])),
        html.Tbody(lignes)
    ], style={"width": "100%", "borderCollapse": "collapse"})

    pagination = html.Div([
        html.Button("⏮️", id="dash-prev", n_clicks=0, disabled=(page == 1)),
        html.Span(f" Page {page} / {pages_totales} ", style={"margin": "0 10px"}),
        html.Button("⏭️", id="dash-next", n_clicks=0, disabled=(page == pages_totales)),
    ])

    return tableau, pagination
