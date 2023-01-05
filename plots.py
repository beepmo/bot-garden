import plotly.express as px
import plotly.graph_objects as go

import json

with open('map.geojson') as raw_map:
    marauders = json.load(raw_map)


# REQUIRES: attribute is 'Species Count' or 'Genus count'
def chloropleth(attribute, filtered_df):
    fig = px.choropleth(
        # pandas dataframe
        filtered_df,

        # specify column for regions
        locations='Bed',

        # specify column for color intensity
        color=attribute,

        # loaded geojson
        geojson=marauders,

        # featureidkey = 'properties.<location column in csv_pddf, which should be same as property key in geojson>'
        featureidkey='properties.bed',

        # hover_data=['Species Count', 'Genus Count'],
        hover_name='Bed',

        height=500,

        color_continuous_scale='blues',

    )

    # if fitbounds is not set, the entire globe is shown
    fig.update_geos(fitbounds="geojson", visible=True)

    # smooth transition when updated
    fig.update_layout(transition_duration=500)

    # pretty hover
    fig.update_layout(
        hoverlabel=dict(
            font_size=16,
            font_family="Rockwell"
        )
    )

    fig.update_layout(
        autosize=False,
        margin=dict(
            # l=0,
            # r=0,
            b=10,
            t=50,
            # pad=50,
            autoexpand=True
        ),
        width=1220,
        #    height=800,
    )

    return fig


def bar(attribute, filtered_df):
    fig = go.Figure(px.bar(filtered_df,
                           x='Bed',
                           y=attribute,
                           ))

    fig.update_layout(xaxis={'categoryorder': 'total descending'})
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_yaxes(fixedrange=False)

    return fig
