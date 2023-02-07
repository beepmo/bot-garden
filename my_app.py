import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

# my functions
from plots import chloropleth
from plots import bar
from plots import sunburst
from plots import box
from plots import pc_line
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
alltab_genus = 'genus callback'
alltab_gardens = 'gardens callback'
tab1_attribute = 'spotlight attribute callback'

# _______________________________________________________________
# laying it out


app.layout = html.Div(
    children=[

        # space
        html.P(children='', className="space"),

        # top section containing preamble & UBC logo
        html.Div(
            children=[
                html.Img(src=logo_image, className="header-logo",
                         ),
            ],
            className="header",
        ),

        # menu
        html.Div(
            children=[

                # alltab_genus selector
                html.Div(
                    children=[
                        html.Div(children="Genus", className="menu-title"),
                        dcc.Dropdown(
                            id=alltab_genus,
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
                        html.Div(children="Gardens", className="menu-title"),
                        dcc.Dropdown(
                            id=alltab_gardens,
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

            ],
            className="main_menu",
        ),

        # preamble for tabs
        html.Div(
            children=[
                html.P(
                    children='''Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                            ''',
                    className="header-description",
                ),
            ],
            className="tab-header",
        ),

        html.Div([
            dcc.Tabs(children=[
                # tab 1: chloropleth + bar
                dcc.Tab(label='Spotlight', children=[

                    html.Div([
                        dcc.RadioItems(ATTRIBUTES, 'Item Count', id=tab1_attribute, inline=False),
                    ]),

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

                                    html.P(
                                        children='Sunburst plot: relation between labels, geo-records, and recency',
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

                # tab 2: sunburst
                dcc.Tab(label='Interrelation', children=[
                    # preamble for 'history by garden' tab
                    html.Div(
                        children=[
                            html.P(
                                children='''Choose a set of gardens to see a summary of its changes over time.
                                ''',
                                className="header-description",
                            ),
                        ],
                        className="tab-header",
                    ),

                    # menu
                    html.Div(
                        children=[

                            # garden selector
                            html.Div(
                                children=[
                                    html.Div(children="Select Gardens", className="menu-title"),
                                    dcc.Dropdown(
                                        # id=s_gardens,
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
                        ],
                        className="menu",
                    ),

                    # wrapper of linechart card
                    html.Div(
                        children=[
                            html.Div(
                                children=[

                                    dcc.Graph(
                                        figure=pc_line(),
                                    ),

                                    html.P(children='Percent items labelled and geo-recorded over time',
                                           className='fig-description',
                                           ),
                                ],
                                className="card",
                            ),
                        ],
                        className="wrapper",
                    ),

                    # wrapper of linechart card
                    html.Div(
                        children=[
                            html.Div(
                                children=[

                                    dcc.Graph(
                                        figure=pc_line(),
                                    ),

                                    html.P(children='Item and species counts over time',
                                           className='fig-description',
                                           ),
                                ],
                                className="card",
                            ),
                        ],
                        className="wrapper",
                    ),
                ]),

                # tab 3: candle
                dcc.Tab(label='Recency', children=[
                ])
            ]),
        ]),
    ], className="tab-wrapper",
)


@app.callback(
    [
        Output("chloropleth", "figure"),
        Output("bar", "figure"),
        Output("sunburst", "figure"),
        Output("box", "figure")
    ],
    [
        Input(component_id=alltab_genus, component_property='value'),
        Input(component_id=tab1_attribute, component_property="value"),
        Input(component_id=alltab_gardens, component_property="value"),
    ],
)
def plots(genus_index, attribute, gardens):
    gardens = set(gardens)
    filtered_df = filter_bed(CACHE[genus_index], gardens)  # convert list to set
    df_for_box = filter_bed(csv_pddf, gardens)

    return [chloropleth(attribute, filtered_df),
            bar(attribute, filtered_df),
            sunburst(attribute, filtered_df),
            box(attribute, df_for_box),
            ]
    # this callback expects list.


if __name__ == "__main__":
    app.run_server(debug=True)
