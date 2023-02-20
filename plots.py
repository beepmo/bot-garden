import plotly.express as px
import plotly.graph_objects as go
import functools

import json

with open('entire.geojson') as raw_map:
    marauders = json.load(raw_map)

# replace bed hover with hover_name
hover_prep = {'Bed': False}


# complications of percent_handler
def percent_handler(plotter):
    @functools.wraps(plotter)
    def wrapper(attribute,
                df):
        # ____________________________________________________________________________________
        # alter data to make fig: add counts and format percentages
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

        # ____________________________________________________________________________________
        # make fig
        fig = plotter(attribute=attribute,
                      df=df)

        # ____________________________________________________________________________________
        # cosmetics for percent_handler sign
        if percent_needed:
            # bar plot
            fig.update_layout(yaxis_ticksuffix='%')
            # chloropleth
            fig.update_coloraxes(colorbar_ticksuffix='%')

        return fig

    return wrapper


# post-processing needed for all plots
def beautify(plotter):
    hover_prep = {'Bed': False}

    @functools.wraps(plotter)
    def wrapper(attribute, df):
        fig = plotter(attribute, df)

        # ____________________________________________________________________________________
        # cosmetics

        # smooth transition when updated
        fig.update_layout(transition_duration=500)

        # pretty hover
        fig.update_layout(
            hoverlabel=dict(
                font_size=16,
                font_family="Rockwell"
            ),
            # title_x=0.5,
            # title_y=0,
        )

        # slider for box and bar plots
        fig.update_layout(xaxis={'categoryorder': 'total descending'})
        fig.update_xaxes(rangeslider_visible=True)
        fig.update_yaxes(fixedrange=False)

        return fig

    return wrapper


# REQUIRES: attribute is 'Species Count' or 'Genus count'
@beautify
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
        featureidkey='properties.b',

        hover_name='Bed',

        height=500,

        color_continuous_scale='blues',

        # decorator
        hover_data=hover_prep,

        # title='Choropleth map: geospatial view of attribute',
    )

    # if fitbounds is not set, the entire globe is shown
    fig.update_geos(fitbounds="geojson", visible=True)

    # make bigger
    fig.update_layout(
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
def bar(attribute, filtered_df):
    fig = go.Figure(px.bar(filtered_df,
                           x='Bed',
                           y=attribute,
                           hover_name='Bed',
                           # decorator
                           hover_data=hover_prep,
                           ))

    return fig


@beautify
# take dummy parameters to appease decorator
def box(attribute, filtered_df):
    fig = px.box(filtered_df,
                 x='Bed',
                 y='Days elapsed since ItemStatusDate',
                 hover_name='Bed')

    return fig


def sunburst(hierarchy, filtered_raw):
    fig = px.sunburst(filtered_raw,
                      path=hierarchy,
                      color='Days elapsed since ItemStatusDate',
                      color_continuous_scale='Teal',
                      range_color=[0, 3650],
                      )
    fig.update_traces(hovertemplate="Number of items: %{value}<br>"
                                    "Average number of days elapsed since ItemStatusDate: %{color:.0f}")
    fig.update_layout(coloraxis_colorbar=dict(
        title="Average time elapsed since ItemStatusDats",
        tickvals=[0, 365, 365*3, 365*5, 365*7, 365*9],
        ticktext=["0", "1y", "3y", "5y", "7y", "9y"],
    ))
    return fig
