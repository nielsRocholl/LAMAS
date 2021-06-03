import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--nodes', type=int, help='Number of nodes', default=10)
parser.add_argument('-c', '--connectivity', type=int, help='Connectivity of graph', default=2)

'''
Class that holds the graph, it uses networkx to create/alter/visualize the graph
'''


class Graph:
    def __init__(self, nodes, connectivity):
        self.number_of_nodes = nodes
        self.connectivity = connectivity
        self.G = self.create_graph()
        self.node_pos = nx.spring_layout(self.G, seed=self.number_of_nodes)  # stores position of nodes
        self.color_map = np.empty(nodes, str)  # stores node colors, needed for draw()
        self.all_nodes_infected = False
        self.infected = [1]
        self.init_node_data()

    def create_graph(self):
        # create graph
        G = nx.Graph()

        # add nodes
        G.add_nodes_from(range(self.number_of_nodes))

        # add edges according to connectivity
        for node in range(self.number_of_nodes):
            for i in range(self.connectivity):
                G.add_edge(node, np.random.randint(self.number_of_nodes))
        return G

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
    'pos' makes sure the nodes keep the same position when drawn
    '''

    def draw_graph(self):
        self.update_color_map()
        nx.draw(self.G, node_color=self.color_map, with_labels=True, pos=self.node_pos)
        plt.show(block=False)
        plt.pause(1)
        plt.close()

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
    Simple function that draws the infected nodes over time
    '''

    def plot_data(self):
        plt.clf()
        plt.ylabel('Infected nodes')
        plt.xlabel('Time step')
        plt.title('Infected nodes over time')
        plt.plot(self.infected, label='Infected Nodes')
        plt.legend()
        plt.show()


'''
Simulate virus spreading
'''


def simulate(nodes, connectivity):
    random = np.random.randint(nodes)

    G = Graph(nodes, connectivity)
    G.infect_node(random)

    while not G.all_nodes_infected:
        G.draw_graph()
        G.update()
    G.plot_data()


def main():
    args = parser.parse_args()
    simulate(args.nodes, args.connectivity)


if __name__ == '__main__':
    main()
