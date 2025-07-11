# stats.py : Visualisation des statistiques

import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from common import lire_conf, lire_table

dash.register_page(__name__, path="/stats", name="📈 STATS - Métriques")

config = lire_conf()
db_path = config.get("db_path", "db/scraper_data.db")

# ===============================
# Données : CONTENU_RECUPERE
# ===============================
try:
    df_contenus = lire_table("SELECT mots_cles, site FROM CONTENU_RECUPERE", db_path=db_path)
except Exception:
    df_contenus = pd.DataFrame()

# Graphique 1 : Mots-clés les plus fréquents
try:
    mots_freq = {}
    if 'mots_cles' in df_contenus.columns:
        for ligne in df_contenus['mots_cles'].dropna():
            for mot in ligne.split(','):
                mot = mot.strip()
                if mot:
                    mots_freq[mot] = mots_freq.get(mot, 0) + 1

                                  

    mots_df = pd.DataFrame(list(mots_freq.items()), columns=['Mot-clé', 'Occurrences'])
    mots_df = mots_df.sort_values(by='Occurrences', ascending=False)

    fig_mots = px.bar(
        mots_df,
        x='Occurrences',
        y='Mot-clé',
        orientation='h',
        title='Mots-clés les plus fréquents',
        height=800  # Agrandit pour tout afficher
    )
    fig_mots.update_layout(yaxis=dict(categoryorder="total ascending"))  # Le plus fréquent en haut
except Exception as e:
    fig_mots = px.bar(title=f"Erreur mots-clés : {e}")

# Graphique 2 : Répartition des contenus récupérés par site
try:
    if 'site' in df_contenus.columns:
        site_count = df_contenus['site'].value_counts().reset_index()
        site_count.columns = ['site', 'count']
        fig_sites = px.pie(
            site_count,
            names='site',
            values='count',
            title='Répartition des contenus récupérés par site'
        )
    else:
        fig_sites = px.pie(title="Colonne 'site' absente")
except Exception as e:
    fig_sites = px.pie(title=f"Erreur site : {e}")

# ===============================
# Données : PAGE_VISITEE
# ===============================
try:
    df_visites = lire_table("SELECT url, profondeur, date_visite FROM PAGE_VISITEE", db_path=db_path)
except Exception:
    df_visites = pd.DataFrame()

# Graphique 3 : Répartition des pages visitées par domaine
try:
    if 'url' in df_visites.columns:
        df_visites['domaine'] = df_visites['url'].apply(lambda x: x.split('/')[2] if '//' in x else x)
        domaine_count = df_visites['domaine'].value_counts().reset_index()
        domaine_count.columns = ['domaine', 'count']
        fig_domaines = px.pie(
            domaine_count,
            names='domaine',
            values='count',
            title='Répartition des pages visitées par domaine'
        )
    else:
        fig_domaines = px.pie(title="Colonne 'url' absente")
except Exception as e:
    fig_domaines = px.pie(title=f"Erreur domaines : {e}")

# Graphique 4 : Chronologie des visites (barres)
try:
    if 'date_visite' in df_visites.columns:
        df_visites['date_visite'] = pd.to_datetime(df_visites['date_visite'], errors='coerce')
        df_visites = df_visites.dropna(subset=['date_visite'])
        df_visites['heure'] = df_visites['date_visite'].dt.floor('h')  # ⏱️ groupement par heure
        timeline = df_visites.groupby('heure').size().reset_index(name='Visites')
        fig_timeline = px.bar(
            timeline,
            x='heure',
            y='Visites',
            title='Nombre de visites par heure'
        )
    else:
        fig_timeline = px.bar(title="Colonne 'date_visite' absente")
except Exception as e:
    fig_timeline = px.bar(title=f"Erreur chronologie : {e}")


# Graphique 5 : Pages visitées par profondeur (barres triées)
try:
    if 'profondeur' in df_visites.columns:
        profondeur_count = df_visites['profondeur'].value_counts().reset_index()
        profondeur_count.columns = ['profondeur', 'count']
        profondeur_count = profondeur_count.sort_values(by='profondeur')
        fig_profondeur = px.bar(
            profondeur_count,
            x='profondeur',
            y='count',
            title='Pages visitées par profondeur',
            labels={'profondeur': 'Profondeur', 'count': 'Pages'}
        )
        fig_profondeur.update_layout(xaxis=dict(categoryorder="category ascending"))
    else:
        fig_profondeur = px.bar(title="Colonne 'profondeur' absente")
except Exception as e:
    fig_profondeur = px.bar(title=f"Erreur profondeur : {e}")

# ===============================
# Layout final
# ===============================
layout = html.Div([
    html.H2("📈 Statistiques d'exploration"),
    dcc.Graph(figure=fig_mots),
    dcc.Graph(figure=fig_sites),
    dcc.Graph(figure=fig_domaines),
    dcc.Graph(figure=fig_timeline),
    dcc.Graph(figure=fig_profondeur)
])
