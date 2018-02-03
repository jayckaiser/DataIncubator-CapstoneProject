#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
GraphPlotting.py

This code provides the means to read in and plot frequency data.

(C) 2018 by Jay Kaiser <jayckaiser.github.io>
Updated Jan 25, 2018

"""

import pandas as pd
import os
from datetime import datetime
from bokeh.plotting import figure, save, output_file, show
from bokeh.palettes import Dark2_5 as palette
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.models.tools import HoverTool
from bokeh.models import ColumnDataSource
from bokeh.embed import components


default_s = ['the_donald', 'hillaryclinton']
default_k = ['trump', 'clinton']

def create_teh_dataframe(data_directory, subreddits=default_s, keywords=default_k):

    # the total is always the first list!
    keywords.insert(0, 'total')

    subreddit_dfs = []

    for sub in subreddits:
        sub_df = pd.read_csv(os.path.join(data_directory, sub + '.csv'), index_col=False)

        sub_df = sub_df.reset_index(level=0, drop=True)

        sub_df['date'] = pd.to_datetime(sub_df['date'])

        sub_df.set_index('date', inplace=True)

        sub_keyword_dfs = []
        for keyword in keywords:
            sub_keyword_dfs.append(sub_df[keyword])

        subreddit_dfs.append(sub_keyword_dfs)

    # zip apart the subreddits for easier plotting
    keyword_zips = list(zip(*subreddit_dfs))

    master_dfs = []
    for keyword_zip in keyword_zips:
        master_dfs.append(pd.DataFrame(dict(zip(subreddits, keyword_zip))))

    return master_dfs


def normalize_dataframes(dataframe_list):
    graphable_dataframes = []

    for df in dataframe_list[1:]:
        normalized_df = df / dataframe_list[0]
        graphable_dataframes.append(normalized_df)

    return graphable_dataframes


def set_starts_and_ends(datetime_list, datetimestart, datetimeend):
    return [ df[ (df.index >= datetimestart) & (df.index <= datetimeend)]
            for df in datetime_list ]


def find_difference(graphable_dataframes, subreddits):
    differenced_dataframes = []

    for df in graphable_dataframes[:]:
        difference_df = pd.DataFrame()

        difference_df[subreddits[0]] = df[subreddits[0]].fillna(0) - df[subreddits[1]].fillna(0)

        differenced_dataframes.append(difference_df)

    return differenced_dataframes


def cumsum_dfs(graphable_dataframes, subreddits):
    cumsummed_dfs = []

    for df in graphable_dataframes:
        new_columns = []

        for sub in subreddits:
            sub_content = df[sub].cumsum()
            new_columns.append(sub_content)

        new_df = pd.DataFrame(dict(zip(subreddits, new_columns), index=df.index))

        cumsummed_dfs.append(new_df)

    return cumsummed_dfs


def remove_outliers_from_df(graphable_dfs, subreddits, q=0.99):
    if q is True:
        q = 0.99

    removed_outliers_list = []

    for df in graphable_dfs:
        max_q = max([df[sub].quantile(q) for sub in subreddits])

        build_query = ' and '.join(['{} < {}'.format(subreddits[i], max_q) for i in range(len(subreddits))])
        minus_outliers = df.query(build_query)

        removed_outliers_list.append(minus_outliers)

    return removed_outliers_list


def smoothify(graphable_dataframes, smoothing_rate=10):
    smoothed_dfs = []

    for df in graphable_dataframes:

        smoothed_df = df.resample('1d').sum().fillna(0).rolling(window=smoothing_rate, min_periods=1).mean()

        smoothed_dfs.append(smoothed_df)

    return smoothed_dfs


def make_dataframes_graphable(dataframe_list, subreddits=default_s, datetimestart=None, datetimeend=None, normalize=False, difference=False, cumsum=False, quantile=0.0, smooth=0.0):
    """
    Plot the frequency data into a graph, with many parameters for customization.

    :Required_params:
    - dataframe_list: a list of dataframes of frequencies, as retrieved in create_teh_dataframe
    - subreddits: a list of subreddits present in the dataframe_list

    :Optional_params:
    - datetimestart: a Datetime object (or None) representing the nearest start date for plotting
    - datetimeend: a Datetime object (or None) representing the nearest end date for plotting
    - normalize: takes the counts for each dataframe and divides by the totals, then removes outliers (True/False)
    - difference: takes the counts for each dataframe of one subreddit minus the other (True/False) REQUIRES 2 DFs!
    - cumsum: takes the cumulative sum for each dataframe (True/False)
    - quantile: marks the quantile from which outliers above will be removed

    :Future_params:
    - smooth:

    """

    if not datetimestart:
        datetimestart = list(dataframe_list[0].index)[0]

    if not datetimeend:
        datetimeend = list(dataframe_list[0].index)[-1]

    # we cannot take a difference of a single column
    if len(dataframe_list[0].columns) != 2:
        difference = False

    # smoothing is unnecessary when cumulative-summing
    if cumsum:
        smooth = 0


    # we can normalize each count by the total number of comments
    if normalize:  # divide each dataframe by its total
        graphable_dataframes = normalize_dataframes(dataframe_list)

    else:
        graphable_dataframes = dataframe_list[1:]  # remove the total from the dataframes

    graphable_dataframes = set_starts_and_ends(graphable_dataframes, datetimestart, datetimeend)

    # this division can result in some crazy outliers....
    if quantile:
        graphable_dataframes = remove_outliers_from_df(graphable_dataframes, subreddits, quantile)

    # maybe we want the cumulative sum?
    if cumsum:
        graphable_dataframes = cumsum_dfs(graphable_dataframes, subreddits)

    # if 2 dataframes, we can take the difference of one's counts from the other's
    if difference:
        graphable_dataframes = find_difference(graphable_dataframes, subreddits)

    if smooth:
        graphable_dataframes = smoothify(graphable_dataframes, smooth)

    return graphable_dataframes


def plot_teh_graphs_bokeh(graphable_dataframes, subreddits, keywords, difference=False):
    colors = list(palette)

    p = figure(plot_width=800, plot_height=800, x_axis_type='datetime', tools="pan,wheel_zoom,box_zoom,reset,hover")

    for i, df in enumerate(graphable_dataframes):

        df['viewable_dates'] = [x.strftime("%Y-%m-%d") for x in df.index]

        df = df.reset_index()

        if difference:

            name = 'r/{} - r/{}: "{}"'.format(subreddits[0], subreddits[1], keywords[i + 1])
            p.line(x='date', y=subreddits[0], source=ColumnDataSource(df),
                   legend=name, color=colors[i])

        else:
            for j, sub in enumerate(subreddits):
                name = 'r/{}: "{}"'.format(subreddits[j], keywords[i + 1])
                p.line(x='date', y=sub, source=ColumnDataSource(df),
                       legend=name, color=colors[len(subreddits) * j + i])

    p.legend.location = "top_left"
    p.legend.click_policy = 'hide'

    hover = p.select(dict(type=HoverTool))
    tips = [('when', '@viewable_dates')]
    hover.tooltips = tips
    hover.mode = 'mouse'

    show(p)
    script, div = components(p)
    return script, div


if __name__ == "__main__":
    data_directory = './data/by_subs_frequencies_100/'

    subreddits = [
        'the_donald',
        'hillaryclinton',
        #'politics'
                  ]
    keywords = [
        'trump',
        'clinton',
        #'sanders'
                ]

    combined_df = create_teh_dataframe(data_directory, subreddits=subreddits, keywords=keywords)

    difference = False

    plot_these = make_dataframes_graphable(combined_df, subreddits,
                                           datetimestart=None,  #datetime(2016, 10, 1),
                                           datetimeend=None,  #datetime(2017, 5, 30),
                                           normalize=False,
                                           difference=difference,
                                           cumsum=False,
                                           quantile=0.99,
                                           smooth=10
                                           )
    #plot_teh_graphs_matplotlib(plot_these, subreddits, keywords, difference=difference)
    plot_teh_graphs_bokeh(plot_these, subreddits, keywords, difference=difference)
