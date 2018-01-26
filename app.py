"""

Jay Kaiser

app.py

Created 12/23/2017

"""

import os
from flask import Flask, render_template, request
from bokeh.plotting import figure
from bokeh.embed import components
from datetime import date
from dateutil.relativedelta import relativedelta
import GraphPlotting

app = Flask(__name__)


@app.route('/')
def to_main_page():
    return render_template('frequencies.html')


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

        startdate = request.form.get('startdate')
        enddate = request.form.get('enddate')

        print(subs2plot)
        print(words2plot)
        print(options2plot)

        # Plotting the graph.
        data_directory = './data/by_subs_frequencies_100/'

        combined_df = GraphPlotting.create_teh_dataframe(data_directory, subreddits=subs2plot, keywords=words2plot)

        difference = False

        plot_these =  GraphPlotting.make_dataframes_graphable(combined_df, subs2plot,
                                                             datetimestart=startdate, datetimeend=enddate,
                                                             **options2plot
                                                             )
        script, div = GraphPlotting.plot_teh_graphs_bokeh(plot_these, subs2plot, words2plot, difference=difference)
        return render_template("graph.html", script=script, div=div)


@app.route('/networks', methods=['GET', 'POST'])
def networks_run():
    pass


def retrieve_options():
    return request.values.getlist('option')


def retrieve_subreddits():
    return request.values.getlist('sub_select')


def retrieve_keywords():
    return request.getlist('keyword_select')


def convert_datetimes(datetime):
    pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))    
    app.run(host='0.0.0.0', port=port)

