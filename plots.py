import plotly.express as px
import plotly.graph_objects as go
import functools

import json

with open('entire.geojson') as raw_map:
    marauders = json.load(raw_map)

hover_prep = {'Bed': False}


def beautify(plotter):
    @functools.wraps(plotter)
    def wrapper(attribute, df):
        percent_needed = attribute == 'Label Stats' or attribute == 'Geo-record Stats'

        # make hoverdata from attribute
        if percent_needed:
            hover_prep.update({
                'Label Stats': False,
                'Geo-record Stats': False,
                '% Labelled': (':.0%', df['Label Stats'] / 100),
                '# Labelled': (':.0f', df['Label Stats'] / 100 * df['Item Count']),
                'Geo-recorded': (':.0%', df['Geo-record Stats'] / 100),
                '# Geo-recorded': (':.0f', df['Geo-record Stats'] / 100 * df['Item Count']),
            })

            # run plot
            fig = plotter(attribute, df, hover_prep)

            # bar plot
            fig.update_layout(yaxis_ticksuffix='%')
            # chloropleth
            fig.update_coloraxes(colorbar_ticksuffix='%')

        else:
            # run plot
            fig = plotter(attribute, df, hover_prep)

        # smooth transition when updated
        fig.update_layout(transition_duration=500)

        # pretty hover
        fig.update_layout(
            hoverlabel=dict(
                font_size=16,
                font_family="Rockwell"
            ),
        )

        return fig

    return wrapper


# REQUIRES: attribute is 'Species Count' or 'Genus count'
@beautify
def chloropleth(attribute, filtered_df, hover_prep):
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
        featureidkey='properties.b',

        hover_name='Bed',

        height=500,

        color_continuous_scale='blues',

        # decorator
        hover_data=hover_prep,
    )

    # if fitbounds is not set, the entire globe is shown
    fig.update_geos(fitbounds="geojson", visible=True)

    # make bigger
    fig.update_layout(
        autosize=False,
        margin=dict(
            # l=0,
            # r=0,
            b=10,
            t=30,
            # pad=50,
            autoexpand=True
        ),
        # width=1220,
        height=650,
    )

    return fig


@beautify
def bar(attribute, filtered_df, hover_prep):
    fig = go.Figure(px.bar(filtered_df,
                           x='Bed',
                           y=attribute,
                           hover_name='Bed',
                           # decorator
                           hover_data=hover_prep,
                           ))

    fig.update_layout(xaxis={'categoryorder': 'total descending'})
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_yaxes(fixedrange=False)

    return fig


import parse_data as pard


def sunburst(filtered_df):
    names = [pard.ITEMS, pard.NOT_L_NOR_G, pard.G_ONLY, pard.L_AND_G, pard.LGPF, pard.L_ONLY]

    sunburst_df = filtered_df[names]

    sum = sunburst_df.sum()

    sunburst_data = dict(
        names=(pard.ITEMS, pard.NOT_L_NOR_G, pard.G_ONLY, pard.L_AND_G, pard.LGPF, pard.L_ONLY),
        parents=('', 'Item Count', 'Item Count', 'Item Count', pard.L_AND_G, 'Item Count'),
        count=sum,
        # color_discrete_map=('blue','gold','darkblue','cyan','yellow'),
    )

    fig = px.sunburst(
        sunburst_data,
        names='names',
        parents='parents',
        values='count',
        template='ggplot2',
        hover_data={'parents': False},
    )

    return fig


from request_csv import csv_pddf


def box(filtered_df):
    fig = px.box(csv_pddf, x='Bed', y='Days Since Sighted')

    fig.update_layout(xaxis={'categoryorder': 'total descending'})
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_yaxes(fixedrange=False)

    return fig
