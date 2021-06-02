import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def main():
    G = nx.complete_graph(10)
    nx.set_node_attributes(G, False, "infected")

    color_map = []
    for node in G.nodes:
        if G.nodes[node]['infected']:
            color_map.append('red')
        else:
            color_map.append('green')

    nx.draw(G, node_color=color_map)


if __name__ == '__main__':
    main()
