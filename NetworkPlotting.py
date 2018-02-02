#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
NetworkPlotting.py

This code provides the means to read in and plot frequency data.

(C) 2018 by Jay Kaiser <jayckaiser.github.io>
Updated Jan 26, 2018

"""

import networkx as nx
import os
import pickle
import matplotlib.pyplot as plt


def load_in_the_graph(directory, file):
    with open(os.path.join(directory, file), 'rb') as FILE:
        return pickle.load(FILE)


def create_subset_graph(G, values2names):
    G = nx.relabel_nodes(G, values2names)
    politics_edges = G.edges(nbunch=['politics'], data=True)

    sorted_edges = []
    for a, b, data in sorted(politics_edges, key=lambda x: x[2]['weight'], reverse=True):
        if data['weight'] > 500:
            sorted_edges.append((a, b, {'weight': data['weight']}))

    sorted_nodes = [e[1] for e in sorted_edges]

    shallow_graph = nx.Graph(sorted_edges)

    edge_labels = {}
    for edge in sorted_edges:
        (a, b, c) = edge
        edge_labels[(a, b)] = c['weight']

    node_degrees = []

    for edge in sorted_edges:
        node = edge[1]
        n_degree = G.degree(node)
        n_power = 0
        for e in G.edges(node, data=True):
            n_power += e[2]['weight'] * 4

        node_degrees.append(n_power / n_degree)

    nx.draw_networkx(shallow_graph,
                     nodelist=sorted_nodes,
                     edgelist=sorted_edges,
                     node_size=node_degrees)
    nx.draw_networkx_edge_labels(shallow_graph, pos=nx.spring_layout(shallow_graph), edge_labels=edge_labels)

    fig = plt.gcf()
    fig.set_size_inches(20, 20)
    plt.show()


if __name__ == "__main__":
    main_directory = '/home/jayckaiser/Documents/jayckaiser-reddit-politics-heroku/data/'
    graphs_directory = os.path.join(main_directory, 'user_graphs/')

    #test_file = 'RC_2014-10.pkl'
    test_file = 'RC_2017-11.pkl'

    G, names2values, values2names = load_in_the_graph(graphs_directory, test_file)
    create_subset_graph(G, values2names)