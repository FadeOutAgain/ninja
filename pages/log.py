# pages/log.py : Affichage en temps réel des logs de NINJA

import dash
from dash import html, dcc, Output, Input
import os
from common import lire_conf

# Enregistrement de la page Log
dash.register_page(__name__, path="/log", name="📜 Log")

# Chargement de la configuration
config = lire_conf()
log_path = config.get("log_file", "logs/ninja.log")
refresh_interval = int(config.get("log_refresh", 2000))

# Mise en page
layout = html.Div([
    html.H4("Derniers logs du scrapper NINJA"),
    html.Pre(id="log-output", style={
        "backgroundColor": "#111",
        "color": "#0f0",
        "padding": "10px",
        "borderRadius": "10px",
        "maxHeight": "500px",
        "overflowY": "scroll",
        "fontSize": "12px",
        "whiteSpace": "pre-wrap",
        "textAlign": "left"
    }),
    dcc.Interval(id="log-refresh", interval=refresh_interval, n_intervals=0)
])

# Callback pour réactualiser le contenu du log
@dash.callback(
    Output("log-output", "children"),
    Input("log-refresh", "n_intervals")
)
def rafraichir_log(_):
    if not os.path.exists(log_path):
        return "> Aucun fichier log trouvé"
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            lignes = f.readlines()[-15:]
            return "".join(lignes)
    except Exception as e:
        return f"> Erreur de lecture du fichier log : {e}"
