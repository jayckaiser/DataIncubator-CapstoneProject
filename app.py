"""

Jay Kaiser

app.py

Created 12/23/2017

"""

import os
from flask import Flask, render_template, request
from datetime import datetime
import GraphPlotting

app = Flask(__name__)


@app.route('/')
def to_main_page():
    return render_template('index.html')


@app.route('/index', methods=['GET', 'POST'])
def index_run():
    """
    Runs the actual server as necessary.

    :return:
    """
    return render_template('index.html')


@app.route('/frequencies', methods=['GET', 'POST'])
def frequencies_run():
    """
    Runs the actual server as necessary.

    :return:
    """
    if request.method == 'GET':
        print('Getting the webpage!')
        return render_template('frequencies.html')

    else:
        print("Let's collect some data!")

        # Retrieving the variables to plot.
        subs2plot = retrieve_subreddits()
        words2plot = retrieve_keywords()
        options2plot = retrieve_options()

        # in the case of errors or missing values...
        if len(subs2plot) == 0:
            subs2plot = ['the_donald', 'hillaryclinton']

        if len(words2plot) == 0:
            words2plot = ['trump', 'clinton']

        print('Subreddits to plot: '.format(' '.join(subs2plot)))
        print('Keywords to plot: '.format(' '.join(words2plot)))
        print('Additional options to plot: '.format(' '.join(options2plot)))

        # Retrieve custom start and end dates.
        try:
            startdate = convert_datetimes(request.form.get('startdate'))
        except ValueError:
            startdate = datetime(2011, 10, 1)

        try:
            enddate = convert_datetimes(request.form.get('enddate'))
        except ValueError:
            enddate = datetime(2017, 12, 30)

        # Plotting the graph.
        data_directory = './data/by_subs_frequencies_100/'

        combined_df = GraphPlotting.create_teh_dataframe(data_directory, subreddits=subs2plot, keywords=words2plot)

        plot_options = {opt: True for opt in options2plot}

        difference = ('difference' in plot_options)

        plot_these = GraphPlotting.make_dataframes_graphable(combined_df, subs2plot,
                                                             datetimestart=startdate, datetimeend=enddate,
                                                             **plot_options
                                                              )
        script, div = GraphPlotting.plot_teh_graphs_bokeh(plot_these, subs2plot, words2plot, difference=difference)
        return render_template("graph.html", script=script, div=div)


@app.route('/rankings', methods=['GET', 'POST'])
def rankings_run():
    return render_template('rankings.html')

@app.route('/normalizedrankings', methods=['GET', 'POST'])
def normalized_rankings_run():
    return render_template('normalizedrankings.html')

@app.route('/counts', methods=['GET', 'POST'])
def counts_run():
    return render_template('counts.html')

@app.route('/normalizedcounts', methods=['GET', 'POST'])
def normalized_counts_run():
    return render_template('normalizedcounts.html')


# Functions used above.

def retrieve_options():
    return request.values.getlist('option')


def retrieve_subreddits():
    return request.values.getlist('sub_select')


def retrieve_keywords():
    return request.values.getlist('keyword_select')


def convert_datetimes(dt):
    return datetime.strptime(dt, '%Y-%m-%d')


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))    
    app.run(host='0.0.0.0', port=port)

