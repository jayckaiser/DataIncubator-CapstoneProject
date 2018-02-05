#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
UsersPlotting.py

This code provides the means to read in and plot subreddit user data.

(C) 2018 by Jay Kaiser <jayckaiser.github.io>
Updated Jan 25, 2018

"""

import pandas as pd
import os
import pickle
import math
import itertools as it
from datetime import datetime
from bokeh.plotting import figure, show
from bokeh.palettes import Dark2_5 as palette
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.models.tools import HoverTool
from bokeh.models import ColumnDataSource, Legend


def extract_dataframe(main_directory):
    datelist = []
    dictionary_dict = {}
    totals = []

    for file in sorted(os.listdir(main_directory)):
        date = datetime.date(datetime.strptime(file[3:-4], '%Y-%m'))
        datelist.append(date)

        with open(os.path.join(main_directory, file), 'rb') as FILE:
            date_dict, total = pickle.load(FILE)

            dictionary_dict[date] = date_dict
            totals.append(total)

    dictionary_df = pd.DataFrame(dictionary_dict)
    #totals_df = pd.Series(totals_dict)

    #dictionary_df['total'] = totals_df

    return (dictionary_df / totals)


def refine_df(df, threshold=0.03275):
    return df[ (df > threshold).any(axis=1) ]


def sort_df(df):
    df['sum'] = df.sum(axis=1)

    df = df.sort_values(by='sum', ascending=False)

    return df


def rank_df(df):
    return df.T.rank(ascending=False).T


def plot_teh_graphs_bokeh(df, per_row=40):

    colors = iter(it.cycle(palette))

    p = figure(plot_width=1700, plot_height=900, x_axis_type='datetime', tools="pan,wheel_zoom,box_zoom,reset",)

    lines = {}

    sub_colors = {}

    for subreddit in df.columns:
        color = next(colors)
        sub_colors[subreddit] = color

        lines[subreddit] = p.line(df.index.values, df[subreddit], alpha=0.1, muted_alpha=1.0,
                                  muted_color=color
                                  #legend=subreddit
                                  )

    num_columns = math.ceil(len(df.columns) / per_row)

    tupled_lines = [ [(k, [lines[k]]) for k in list(lines.keys())[i*per_row : min((i+1)*per_row, len(df.columns))] ]
                     for i in range(num_columns)]

    for i, column in enumerate(tupled_lines):
        legend = Legend(items=tupled_lines[i], spacing=0, padding=0,
                        click_policy='mute', inactive_fill_alpha=0.6)
        p.add_layout(legend, 'right')

    p.yaxis.visible = False
    p.ygrid.visible = False
    p.legend.border_line_alpha = 0.0
    p.legend.background_fill_alpha = 0.1

    show(p)
    #script, div = components(p)
    #return script, div


def create_dataframe(directory, relative=True):
    df = extract_dataframe(directory)

    df = refine_df(df)
    print(len(df))

    df = sort_df(df).T

    if relative:
        df = rank_df(df)
        df = -1 * df

    return df


if __name__ == "__main__":
    main_directory = './data/subreddit_counts/'

    df = create_dataframe(main_directory, relative=False)
    #print(df)

    plot_teh_graphs_bokeh(df)

    #print(refined_df.info)
