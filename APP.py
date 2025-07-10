# APP.py

import dash
from dash import html, dcc
from dash.dependencies import Input, Output

app = dash.Dash(__name__, use_pages=True, suppress_callback_exceptions=True)
app.title = "🥷️ NINJA - Interface"

app.layout = html.Div([
    # Police Roboto depuis Google Fonts
    html.Link(
        rel="stylesheet",
        href="https://fonts.googleapis.com/css2?family=Roboto&display=swap"
    ),

    html.Div([
        html.H1("️🥷 NINJA", style={"textAlign": "center"}),

        dcc.Tabs(
            id="tabs",
            value=list(dash.page_registry.keys())[0],
            children=[
                dcc.Tab(label=page["name"], value=key)
                for key, page in dash.page_registry.items()
            ]
        ),

        html.Div(id="page-content", style={"padding": "20px"})
    ], style={"fontFamily": "Roboto, sans-serif"})
])

@app.callback(
    Output("page-content", "children"),
    Input("tabs", "value")
)
def afficher_page(tab_value):
    return dash.page_registry[tab_value]["layout"]

if __name__ == "__main__":
    app.run(debug=True)
