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


# selection options & THE DATA
from parse_data import CONCISE_ATTRIBUTES, GENUS, CONCISE_CACHE, RAW_CACHE
from request_csv import RAW_ATTRIBUTES

# plotted regions in geojson
from filter_data import GARDENS

# callback id
alltab_genus = 'genus callback'
alltab_gardens = 'gardens callback'
tab1_attribute = 'spotlight attribute callback'
tab2_hierarchy = 'hierarchy for sunburst path'
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
                            value=(GARDENS[0]),  # 'All gardens'
                            clearable=True,
                            searchable=True,
                            multi=True,
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
                    children='''UBC Botanical Garden Collections Data Dashboard
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
                        dcc.RadioItems([
                            {
                                "label": "🍁 Item Count",
                                "value": "Item Count",
                            },
                            {
                                "label": "🧬 Species Count",
                                "value": "Species Count",
                            },
                            {
                                "label": "📝 Label Stats",
                                "value": "Label Stats",
                            },
                            {
                                "label": "⚓️ Geo-record Stats",
                                "value": "Geo-record Stats",
                            },
                        ],
                            value='Item Count',
                            id=tab1_attribute, inline=True,
                            inputStyle={"margin-left": "30px", "margin-right": "30px"}),
                    ], className="radio"),

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

                ]),

                # tab 2: sunburst
                dcc.Tab(label='Interrelation', children=[

                    # hierarchy selector
                    html.Div(
                        children=[
                            html.Div(children="Hierarchy", className="menu-title"),
                            dcc.Dropdown(
                                id=tab2_hierarchy,
                                options=['Bed', 'Label', 'Geo?', 'Taxon'],
                                value=['Label', 'Geo?'],
                                searchable=True,
                                clearable=True,
                                multi=True,
                                style={
                                    'width': '100%'
                                }
                            ),
                        ], className='radio'
                    ),

                    # wrapper of sunburst card
                    html.Div(
                        children=[
                            html.Div(
                                children=[

                                    # sunburst plot
                                    dcc.Graph(
                                        id="sunburst", config={"displayModeBar": True},
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

                    # wrapper of box card
                    html.Div(
                        children=[
                            html.Div(
                                children=[

                                    # box plot
                                    dcc.Graph(
                                        id="box", config={"displayModeBar": True},
                                    ),
                                ],
                                className="card",
                            ),
                        ],
                        className="wrapper",
                    ),

                ])
            ]),
        ]),

        # bottom band
        html.Div(
            children=[
                html.H1(children=''),
                html.P(children="🥑", className="header-emoji"),
                html.H1(children=''),
            ],
            className="header",
        ),
    ], className="tab-wrapper",
)


@app.callback(
    [
        Output("chloropleth", "figure"),
        Output("bar", "figure"),
        Output("box", "figure"),
        Output("sunburst", "figure"),
    ],
    [
        Input(component_id=alltab_genus, component_property='value'),
        Input(component_id=tab1_attribute, component_property="value"),
        Input(component_id=alltab_gardens, component_property="value"),
        Input(component_id=tab2_hierarchy, component_property="value"),
    ],
)
def plots(genus_index, attribute, gardens, hierarchy):
    gardens = set(gardens)
    filtered_concise = filter_bed(CONCISE_CACHE[genus_index], gardens)  # convert list to set
    filtered_raw = filter_bed(RAW_CACHE[genus_index], gardens)

    print(hierarchy)

    return [chloropleth(attribute, filtered_concise),
            bar(attribute, filtered_concise),
            box(attribute, filtered_raw),
            sunburst(hierarchy, filtered_raw)
            ]
    # this callback expects list.


if __name__ == "__main__":
    app.run_server(debug=True)
