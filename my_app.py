import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

# my functions
from plots import chloropleth
from plots import bar
from plots import sunburst
from plots import box
from filter_data import filter_bed

# _______________________________________________________________
# flask

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

# _______________________________________________________________
# variables

# for BOX
from request_csv import csv_pddf

# selection options & THE DATA
from parse_data import ATTRIBUTES, GENUS, CACHE

# plotted regions in geojson
from filter_data import GARDENS

# callback id
s_genus = 'snapshot genus'
s_gardens = 'snapshot set of gardens'
s_attribute = 'snapshot attribute'

# _______________________________________________________________
# laying it out

app.layout = html.Div(
    children=[

        # top section containing preamble & UBC logo
        html.Div(
            children=[
                # html.P(children="🥑", className="header-emoji"),
                html.Img(src=logo_image, className="header-logo",
                         style={'textAlign': 'center'}),
                # html.H3(
                #     children="Botanical Garden", className="header-title"
                # ),
                # TODO left justify
            ],
            className="header",
        ),

        html.Div([
            dcc.Tabs([

                # tab 1: present
                dcc.Tab(label='Snapshot', children=[

                    # preamble for 'present' tab
                    html.Div(
                        children=[
                            # html.P(children="🥑", className="header-emoji"),

                            html.P(
                                children='''Filter by gardens and genus!
                                Specify an attribute to display on the map and bar plots.
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
                                        id=s_genus,
                                        options=[
                                            {"label": GENUS[i], "value": i}
                                            for i in range(0, len(GENUS))
                                        ],
                                        value=0,
                                        searchable=True,
                                        className="dropdown",
                                    ),
                                ],
                            ),

                            # garden selector
                            html.Div(
                                children=[
                                    html.Div(children="Select Gardens", className="menu-title"),
                                    dcc.Dropdown(
                                        id=s_gardens,
                                        options=[
                                            {"label": garden, "value": garden}
                                            for garden in GARDENS
                                        ],
                                        value=('Alpine Garden', 'Winter Garden'),
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
                                        id=s_attribute,
                                        options=[
                                            {"label": attribute, "value": attribute}
                                            for attribute in ATTRIBUTES
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

                                    html.P(children='Choropleth map: geospatial view of attribute',
                                           className='fig-description',
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

                                    html.P(children='Bar chart: sorting by attribute value',
                                           className='fig-description',
                                           ),
                                ],
                                className="card",
                            ),
                        ],
                        className="wrapper",
                    ),

                    # wrapper of sunburst card
                    html.Div(
                        children=[
                            html.Div(
                                children=[

                                    # sunburst plot
                                    dcc.Graph(
                                        id="sunburst", config={"displayModeBar": False},
                                    ),

                                    html.P(children='Sunburst plot: relation between labels, geo-records, and recency',
                                           className='fig-description',
                                           ),
                                ],
                                className="card",
                            ),
                        ],
                        className="wrapper",
                    ),

                    # wrapper of box card
                    html.Div(
                        children=[
                            html.Div(
                                children=[

                                    # box plot
                                    dcc.Graph(
                                        id="box", config={"displayModeBar": True},
                                    ),

                                    html.P(children='Box plot, sorted: where lurk the ancients? '
                                                    '(Genus filter not yet supported!)',
                                           className='fig-description',
                                           ),
                                ],
                                className="card",
                            ),
                        ],
                        className="wrapper",
                    ),

                    # bottom band
                    html.Div(
                        children=[
                            html.H1(children=''),
                            html.P(children="🥑", className="header-emoji"),
                            html.H1(children=''),
                        ],
                        className="header",
                    ),
                ]),

                # tab 2: history by garden
                dcc.Tab(label='History by Garden', children=[
                ]),

                # tab 3: history by genus
                dcc.Tab(label='History by Genus', children=[
                ])
            ])
        ]),
    ]
)


@app.callback(
    [
        Output("chloropleth", "figure"),
        Output("bar", "figure"),
        Output("sunburst", "figure"),
        Output("box", "figure")
    ],
    [
        Input(component_id=s_genus, component_property='value'),
        Input(component_id=s_attribute, component_property="value"),
        Input(component_id=s_gardens, component_property="value"),
    ],
)
def plots(genus_index, attribute, gardens):
    gardens = set(gardens)
    filtered_df = filter_bed(CACHE[genus_index], gardens)  # convert list to set
    df_for_box = filter_bed(csv_pddf, gardens)

    return [chloropleth(attribute, filtered_df),
            bar(attribute, filtered_df),
            sunburst(filtered_df),
            box(df_for_box),
            ]
    # this callback expects list.


if __name__ == "__main__":
    app.run_server(debug=True)
