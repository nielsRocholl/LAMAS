import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--nodes', type=int, help='Number of nodes', default=10)

'''
Class that holds the graph, it uses networkx to create/alter/visualize the graph
'''


class Graph:
    def __init__(self, nodes):
        self.number_of_nodes = nodes
        self.G = nx.complete_graph(nodes)
        self.color_map = np.empty(nodes, str)
        self.all_nodes_infected = False
        self.infected = []
        self.init_node_data()

    '''
    Each node can store data, this function creates a data variable 'infected' and sets it to false
    '''

    def init_node_data(self):
        nx.set_node_attributes(self.G, False, "infected")

    '''
    Networkx needs a color map to draw the graph (with color), this function updates the color map
    '''

    def update_color_map(self):
        for node in self.G.nodes:
            if self.G.nodes[node]['infected']:
                self.color_map[node] = 'red'
            else:
                self.color_map[node] = 'green'

    '''
    Draws the current Graph
    Side note: If you run draw in Google colab you dont need to call plt.show()
    '''

    def draw_graph(self):
        self.update_color_map()
        nx.draw(self.G, node_color=self.color_map, with_labels=True)
        plt.show()

    '''
    Infect a single node
    '''

    def infect_node(self, node):
        if not self.G.nodes[node]['infected']:
            self.G.nodes[node]['infected'] = True

    '''
    Infect all neighboring nodes
    '''

    def infect_all_neighbours(self):
        infected_nodes = [x for x, y in self.G.nodes(data=True) if y['infected']]

        for infected_node in infected_nodes:
            for node in self.G.neighbors(infected_node):
                self.infect_node(node)

    '''
    Count the amount of infected nodes
    '''

    def count_infected(self):
        infected = 0
        for node in self.G.nodes:
            if self.G.nodes[node]['infected']:
                infected += 1

        return infected

    '''
    Update the graph
    '''

    def update(self):
        self.infected.append(self.count_infected())
        self.all_nodes_infected = True if self.count_infected() == self.number_of_nodes else False
        self.infect_all_neighbours()


'''
Simulate virus spreading
'''


def simulate(nodes):
    random = np.random.randint(nodes)

    G = Graph(nodes)
    G.infect_node(random)

    while not G.all_nodes_infected:
        G.draw_graph()
        G.update()


def main():
    args = parser.parse_args()
    simulate(args.nodes)


if __name__ == '__main__':
    main()
