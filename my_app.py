import dash
from dash import dcc
from dash import html
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
                # html.H3(
                #     children="UBC Botanical Garden", className="header-title"
                # ),
                # TODO left justify
            ],
            className="header",
        ),

        html.Div([
            dcc.Tabs([

                # tab 1: throwing numbers
                dcc.Tab(label='Present', children=[

                    # preamble for 'present' tab
                    html.Div(
                        children=[
                            # html.P(children="🥑", className="header-emoji"),

                            html.P(
                                children='''Select gardens, a genus, and an attribute to see their snapshot today.
                                        ''',
                                className="header-description",
                            ),
                        ],
                        className="tab-header",
                    ),

                    # menu
                    html.Div(
                        children=[

                            # genus selector
                            html.Div(
                                children=[
                                    html.Div(children="Genus", className="menu-title"),
                                    dcc.Dropdown(
                                        id="genus-filter",
                                        options=[
                                            {"label": g, "value": g}
                                            for g in genus
                                        ],
                                        value="",
                                        clearable=True,
                                        searchable=True,
                                        className="dropdown",
                                    ),
                                ],
                            ),

                            # garden selector
                            html.Div(
                                children=[
                                    html.Div(children="Select gardens", className="menu-title"),
                                    dcc.Dropdown(
                                        id="beds-filter",
                                        options=[
                                            {"label": garden, "value": garden}
                                            for garden in gardens
                                        ],
                                        value=['Alpine Garden', 'Winter Garden'],
                                        clearable=True,
                                        searchable=True,
                                        multi=True,
                                        className="dropdown",
                                    ),
                                ],
                            ),

                            # attribute selector
                            html.Div(
                                children=[
                                    html.Div(children="Attribute", className="menu-title"),
                                    dcc.Dropdown(
                                        id="attribute-filter",
                                        options=[
                                            {"label": attribute, "value": attribute}
                                            for attribute in attributes
                                        ],
                                        value="Item Count",
                                        className="dropdown",
                                    ),
                                ],
                            ),

                        ],
                        className="menu",
                    ),

                    # wrapper of chloropleth card
                    html.Div(
                        children=[
                            html.Div(
                                children=[

                                    # chloropleth map
                                    dcc.Graph(
                                        id="chloropleth", config={"displayModeBar": True},
                                    ),
                                ],
                                className="card",
                            ),
                        ],
                        className="wrapper",
                    ),

                # wrapper of bar card
                    html.Div(
                        children=[
                            html.Div(
                                children=[

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
                            html.H1(children=''),
                            html.P(children="🥑", className="header-emoji"),
                            html.H1(children=''),
                        ],
                        className="header",
                    ),
                ]),

                # tab 2: spotlight
                dcc.Tab(label='History', children=[
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


gcache = {}


def genus_cache(genus):
    filtered = gcache.get(genus)
    if filtered is None:
        genus_df = parse_genus(genus)
        gcache.update({genus: filtered})
    return genus_df


if __name__ == "__main__":
    app.run_server(debug=True)
