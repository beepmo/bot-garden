import dash
from dash import dcc
from dash import html
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output

# my functions
from plots import chloropleth
from plots import bar
from filter_data import filter_bed
from parse_genus import parse_genus

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.title = "UBC Bot Garden"
logo_image = 'assets/UBC-logo-2018-fullsig-white-rgb72.png'

# set of "throwing" tab dropdown options
from parse_data import attributes

# plotted regions in geojson
from filter_data import gardens

# list of "spotlight" tab options
genus = ['Acer',
         'Magnolia',
         'Rhododendron',
         'Cytisus',
         'Lavendula',
         'Toxicodendron'
         ]

app.layout = html.Div(
    children=[

        # top section containing preamble & UBC logo
        html.Div(
            children=[
                # html.P(children="🥑", className="header-emoji"),
                html.Img(src=logo_image, className="header-logo",
                         style={'textAlign': 'center'}),
                html.H1(
                    children="UBC Botanical Garden", className="header-title"
                ),
                html.H1(children=' '),
                html.P(
                    children='''Otherworldly terrain.
                            Here are some teasers that don't give away too much.
                            ''',
                    className="header-description",
                ),
            ],
            className="header",
        ),

        html.Div([
            dcc.Tabs([

                # tab 1: throwing numbers
                dcc.Tab(label='Throwing numbers', children=[

                    # garden selector
                    html.Div(
                        children=[
                            html.Div(
                                children=[
                                    html.Div(children="Browse gardens", className="menu-title"),
                                    dcc.Dropdown(
                                        id="beds-filter",
                                        options=[
                                            {"label": garden, "value": garden}
                                            for garden in gardens
                                        ],
                                        value="All that beep mapped",
                                        clearable=True,
                                        searchable=True,
                                        multi=True,
                                        className="dropdown",
                                    ),
                                ],
                            ),
                        ],
                        className="menu",
                    ),

                    # wrapper contains attribute selector asw chloropleth and bar cards
                    html.Div(
                        children=[
                            html.Div(
                                children=[

                                    # attribute selector
                                    dcc.Dropdown(
                                        id="attribute-filter",
                                        options=[
                                            {"label": attribute, "value": attribute}
                                            for attribute in attributes
                                        ],
                                        value="Species Count",
                                        className="dropdown",
                                    ),

                                    # chloropleth map
                                    dcc.Graph(
                                        id="chloropleth", config={"displayModeBar": True},
                                    ),

                                    # bar plot
                                    dcc.Graph(
                                        id="bar", config={"displayModeBar": True},
                                    ),
                                ],
                                className="card",
                            ),
                        ],
                        className="wrapper",
                    ),

                    # bottom section containing big numbers
                    html.Div(
                        children=[
                            html.P(children="🥑", className="header-emoji"),
                            html.H1(
                                id="big number", className="header-title"
                            ),
                            html.H1(children=' '),
                            html.P(
                                children='''\n\n\n SPECIES  ||  GENUS \n\n
                                ''',
                                className="header-description",
                            ),
                        ],
                        className="header",
                    ),
                ]),

                # tab 2: spotlight
                dcc.Tab(label='Spotlight', children=[
                    html.Div(
                        children=[
                            html.Div(
                                children=[
                                    html.Div(children="Search Genera", className="menu-title"),
                                    dcc.Dropdown(
                                        id="genus-filter",
                                        options=[
                                            {"label": g, "value": g}
                                            for g in genus
                                        ],
                                        value="Cytisus",
                                        clearable=True,
                                        searchable=True,
                                        className="dropdown",
                                    ),
                                ],
                            ),
                        ],
                        className="menu",
                    ),
                    html.Div(
                        children=[
                            html.Div(
                                children=[

                                    dcc.Graph(
                                        id="find family", config={"displayModeBar": True},
                                    ),
                                ],
                                className="card",
                            ),
                        ],
                        className="wrapper",
                    ),
                    html.Div(
                        children=[
                            html.P(children="🥑", className="header-emoji"),
                            html.H1(
                                id="family number", className="header-title"
                            ),
                            html.H1(children=' '),
                            html.P(
                                id="familyname",
                                className="header-description",
                            ),
                        ],
                        className="header",
                    ),
                ])
            ])
        ]),
    ]
)


@app.callback(
    [
        Output("chloropleth", "figure"),
        Output("bar", "figure")
    ],
    [
        Input(component_id="attribute-filter", component_property="value"),
        Input(component_id="beds-filter", component_property="value"),
    ],
)
def plots(attribute, gardens):
    filtered_df = filter_cache(gardens)

    return [chloropleth(attribute, filtered_df), bar(attribute, filtered_df)]
    # this chloropleth expects list. the other doesn't


df_cache = {}


def filter_cache(gardens):
    filtered = df_cache.get(tuple(gardens))
    if filtered is None:
        filtered = filter_bed(gardens)
        df_cache.update({tuple(gardens): filtered})
    return filtered


@app.callback(
    [
        Output("big number", "children")
    ],
    [
        Input(component_id="beds-filter", component_property="value"),
    ]
)
def big_number(gardens):
    filtered_df = filter_cache(gardens)
    species_cnt = filtered_df['Species Count'].sum()
    genus_cnt = filtered_df['Genus Count'].sum()
    return [str(species_cnt) + ' |-------| ' + str(genus_cnt)]


@app.callback(
    [
        Output("find family", "figure"),
        Output("family number", "children"),
        Output("familyname", "children")
    ],
    [Input("genus-filter", "value")]
)
def find_family(genus):
    axis = genus + ' Count'

    genus_df = genus_cache(genus)

    item_cnt = genus_df[axis].sum()

    return chloropleth(axis, genus_df), item_cnt, axis


gcache = {}


def genus_cache(genus):
    filtered = gcache.get(genus)
    if filtered is None:
        genus_df = parse_genus(genus)
        gcache.update({genus: filtered})
    return genus_df


if __name__ == "__main__":
    app.run_server(debug=True)
