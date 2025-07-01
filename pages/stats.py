# stats.py : Visualisation des statistiques

import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from common import lire_conf, lire_table

# Enregistrement de la page Stats
dash.register_page(__name__, path="/stats", name="📈 Stats")

# Récupération du chemin de la base
config = lire_conf()
db_path = config.get("db_path", "db/scraper_data.db")

# Lecture des données de visites
try:
    df_visites = lire_table("SELECT url, profondeur, date_visite FROM PAGE_VISITEE", db_path=db_path)
except Exception as e:
    df_visites = pd.DataFrame()

# Graphique 1 : Nombre de pages visitées par profondeur
try:
    if 'profondeur' in df_visites.columns:
        profondeur_count = df_visites['profondeur'].value_counts().sort_index().reset_index()
        fig_profondeur = px.bar(
            profondeur_count,
            x='index',
            y='profondeur',
            labels={'index': 'Profondeur', 'profondeur': 'Pages'},
            title='Nombre de pages visitées par profondeur'
        )
    else:
        fig_profondeur = px.bar(title="Colonne 'profondeur' absente")
except Exception as e:
    fig_profondeur = px.bar(title=f"Erreur profondeur : {e}")

# Graphique 2 : Répartition des pages visitées par domaine
try:
    if 'url' in df_visites.columns:
        df_visites['domaine'] = df_visites['url'].apply(lambda x: x.split('/')[2] if '//' in x else x)
        domaine_count = df_visites['domaine'].value_counts().reset_index()
        fig_domaines = px.pie(
            domaine_count,
            names='index',
            values='domaine',
            title='Répartition des pages visitées par domaine'
        )
    else:
        fig_domaines = px.pie(title="Colonne 'url' absente")
except Exception as e:
    fig_domaines = px.pie(title=f"Erreur domaines : {e}")

# Graphique 3 : Chronologie des visites
try:
    if 'date' in df_visites.columns:
        df_visites['date'] = pd.to_datetime(df_visites['date'], errors='coerce')
        df_visites = df_visites.dropna(subset=['date'])
        df_visites['heure'] = df_visites['date'].dt.floor('min')
        timeline = df_visites.groupby('heure').size().reset_index(name='Visites')
        fig_timeline = px.line(
            timeline,
            x='heure',
            y='Visites',
            title='Nombre de visites dans le temps'
        )
    else:
        fig_timeline = px.line(title="Colonne 'date' absente")
except Exception as e:
    fig_timeline = px.line(title=f"Erreur chronologie : {e}")

# Layout de la page
layout = html.Div([
    html.H2("📈 Statistiques d'exploration"),
    dcc.Graph(figure=fig_profondeur),
    dcc.Graph(figure=fig_domaines),
    dcc.Graph(figure=fig_timeline)
])
