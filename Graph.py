import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--agents', type=int, help='Number of agents', default=10)
parser.add_argument('-c', '--connectivity', type=int, help='Connectivity of graph', default=2)

'''
Class that holds the graph, it uses networkx to create/alter/visualize the graph
'''


class Graph:
    def __init__(self, agents, connectivity):
        self.number_of_agents = agents
        self.connectivity = connectivity
        self.G = self.create_graph()
        self.node_pos = nx.spring_layout(self.G, seed=self.number_of_agents)  # stores position of nodes
        self.color_map = np.empty(agents, str)  # stores node colors, needed for draw()
        self.all_agents_know = False
        self.rumor_is_known = [1]
        self.E_known = [1]
        self.EE_known = [1]
        self.init_node_data()

    def create_graph(self):
        # create graph
        G = nx.Graph()

        # add nodes
        G.add_nodes_from(range(self.number_of_agents))

        # add edges according to connectivity
        for node in range(self.number_of_agents):
            for i in range(self.connectivity):
                G.add_edge(node, np.random.randint(self.number_of_agents))
        return G

    '''
    Each node can store data, this function creates a data variable 'rumor_is_known' and sets it to false
    '''

    def init_node_data(self):
        nx.set_node_attributes(self.G, False, "rumor_is_known")

        # Everybody knows attributes
        nx.set_node_attributes(self.G, [], "who_knows_list")
        nx.set_node_attributes(self.G, False, "E_knows")
        nx.set_node_attributes(self.G, [], "who_knows_E_knows_list")
        nx.set_node_attributes(self.G, False, "EE_knows")


    '''
    Networkx needs a color map to draw the graph (with color), this function updates the color map
    '''

    def update_color_map(self):
        for node in self.G.nodes:
            if self.G.nodes[node]['rumor_is_known']:
                self.color_map[node] = 'red'
            else:
                self.color_map[node] = 'green'

    '''
    Draws the current Graph
    'pos' makes sure the nodes keep the same position when drawn
    '''

    def draw_graph(self):
        plt.figure(figsize=(9, 7))
        self.update_color_map()
        nx.draw(self.G, node_color=self.color_map, with_labels=True, pos=self.node_pos)
        plt.show(block=False)
        plt.pause(1.5)
        plt.close()

    '''
    Spread rumor to the first agent
    '''

    def spread_rumor_to_first_agent(self, node):
        if not self.G.nodes[node]['rumor_is_known']:
            self.G.nodes[node]['rumor_is_known'] = True

        # I know that I know
        if not self.G.nodes[node]['who_knows_list']:
            self.G.nodes[node]['who_knows_list'] = [node]



    '''
    Spread rumor to a single agent
    '''

    def spread_rumor_to_single_agent(self, node, previous_node):
        if not self.G.nodes[node]['rumor_is_known']:
            self.G.nodes[node]['rumor_is_known'] = True
        
        # Everybody knows rumor spread part
        if not self.G.nodes[node]['who_knows_list']:
            self.G.nodes[node]['who_knows_list'] = [node]

        newList = list( set( self.G.nodes[node]['who_knows_list'] ) | set( self.G.nodes[previous_node]['who_knows_list'] ) )
        self.G.nodes[node]['who_knows_list'] = newList

        if set(self.G.nodes[node]['who_knows_list']) == set(list(self.G.nodes)):
            self.G.nodes[node]['E_knows'] = True
        
        if not self.G.nodes[node]['who_knows_E_knows_list'] and self.G.nodes[node]['E_knows']:
            self.G.nodes[node]['who_knows_E_knows_list'] = [node]

        newList = list( set( self.G.nodes[node]['who_knows_E_knows_list'] ) | set( self.G.nodes[previous_node]['who_knows_E_knows_list'] ) )
        self.G.nodes[node]['who_knows_E_knows_list'] = newList

        if set(self.G.nodes[node]['who_knows_E_knows_list']) == set(list(self.G.nodes)):
            self.G.nodes[node]['EE_knows'] = True

            

    '''
    Spread rumor to all neighboring agents
    '''

    def spread_rumor_to_all_neighbours(self):
        agent_that_know = [x for x, y in self.G.nodes(data=True) if y['rumor_is_known']]

        for knowledgeable_agent in agent_that_know:
            for agent in self.G.neighbors(knowledgeable_agent):
                self.spread_rumor_to_single_agent(agent, knowledgeable_agent)

    '''
    Count the amount of knowledgeable agents
    '''

    def count_knowledgeable(self, knowledge):
        knowledgeable = 0
        for agent in self.G.nodes:
            if self.G.nodes[agent][knowledge]:
                knowledgeable += 1

        return knowledgeable

    '''
    Update the graph
    '''

    def update(self):
        # keep track of knowledge
        self.rumor_is_known.append(self.count_knowledgeable('rumor_is_known'))
        self.E_known.append(self.count_knowledgeable('E_knows'))
        self.EE_known.append(self.count_knowledgeable('EE_knows'))

        # check if termination condition is met
        self.all_agents_know = True if self.count_knowledgeable('EE_knows') == self.number_of_agents else False
        self.spread_rumor_to_all_neighbours()

    '''
    Simple function that draws the knowledgeable agents over time
    '''

    def plot_data(self):
        plt.clf()
        plt.ylabel('Knowledgeable Agents')
        plt.xlabel('Time step')
        plt.title('Knowledgeable agents over time')
        plt.plot(self.rumor_is_known, label='Knowledgeable Agents')
        plt.plot(self.E_known, label='E-Knowledgeable Agents')
        plt.plot(self.EE_known, label='EE-Knowledgeable Agents')
        plt.legend()
        plt.show()


'''
Simulate rumor spreading
'''


def simulate(agents, connectivity):
    random = np.random.randint(agents)

    G = Graph(agents, connectivity)
    G.spread_rumor_to_first_agent(random)

    while not G.all_agents_know:
        G.draw_graph()
        G.update()
    G.plot_data()


def main():
    args = parser.parse_args()
    simulate(args.agents, args.connectivity)


if __name__ == '__main__':
    main()
