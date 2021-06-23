import networkx as nx
import matplotlib.pyplot as plt
from networkx.classes.function import degree
from networkx.readwrite.json_graph import tree
import numpy as np
import argparse
from itertools import repeat, combinations
from string import ascii_lowercase

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--agents', type=int, help='Number of agents', default=10)
parser.add_argument('-c', '--connectivity', type=int, help='Connectivity of graph', default=2)
parser.add_argument('-n', '--degree_of_shared_knowledge', type=int, help='Degree of shared knowledge', default=2)



'''
Class that holds the graph, it uses networkx to create/alter/visualize the graph
'''


class Graph:
    def __init__(self, agents, connectivity, degree_of_shared_knowledge):
        self.number_of_agents = agents
        self.connectivity = connectivity
        self.G = self.create_graph()
        self.node_pos = nx.spring_layout(self.G, seed=self.number_of_agents)  # stores position of nodes
        self.color_map = np.empty(agents, str)  # stores node colors, needed for draw()
        self.all_agents_know = False
        self.degree_of_shared_knowledge = degree_of_shared_knowledge
        self.rumor_is_known = [1]
        self.dynamic_E_known = [[] for x in repeat(None, degree_of_shared_knowledge)]
        self.init_node_data()
        self.labels = {}

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

        # Everybody knows attributes, attribute name is an integer from [0-n]
        for n in range(self.degree_of_shared_knowledge):
            nx.set_node_attributes(self.G, [], str(n))
            nx.set_node_attributes(self.G, [], f'{n}_next_step_knowledge')
            nx.set_node_attributes(self.G, False, f'{n}_knows')

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
        # nx.draw(self.G, node_color=self.color_map, pos=self.node_pos)
        nx.draw_networkx_nodes(self.G, self.node_pos)
        nx.draw_networkx_edges(self.G, self.node_pos)
        # nx.draw_networkx_labels(self.G, self.node_pos, self.labels)
        nx.draw_networkx_labels(self.G, self.node_pos, self.labels, font_size=16)

        plt.show(block=False)
        plt.pause(0.5)
        plt.close()

    '''
    Spread rumor to the first agent
    '''

    def spread_rumor_to_first_agent(self, node):
        if not self.G.nodes[node]['rumor_is_known']:
            self.G.nodes[node]['rumor_is_known'] = True

        # I know that I know
        if not self.G.nodes[node][str(0)]:
            self.G.nodes[node][str(0)] = [node]

    def spread_rumor_to_single_agent2(self, agent, previous_agent):

        if not self.G.nodes[agent]['rumor_is_known']:
            self.G.nodes[agent]['rumor_is_known'] = True

        for n in range(self.degree_of_shared_knowledge):
            if n == 0:
                if not self.G.nodes[agent][f'{n}']:
                    self.G.nodes[agent][f'{n}'] = [agent]

                
                # self.G.nodes[agent][f'{n}'] = self.new_list(agent, previous_agent, n)
                # if set(self.G.nodes[agent][f'{n}']) == set(list(self.G.nodes)):
                #     self.G.nodes[agent][f'{n}_knows'] = True

                self.G.nodes[agent][f'{n}_next_step_knowledge'] = self.new_list(agent, previous_agent, n)

            if n > 0:
                if not self.G.nodes[agent][f'{n}'] and self.G.nodes[agent][f'{n - 1}_knows']:
                    print(n)
                    self.G.nodes[agent][f'{n}'] = [agent]


                # self.G.nodes[agent][f'{n}'] = self.new_list(agent, previous_agent, n)
                # if set(self.G.nodes[agent][f'{n}']) == set(list(self.G.nodes)):
                #     self.G.nodes[agent][f'{n}_knows'] = True


                self.G.nodes[agent][f'{n}_next_step_knowledge'] = self.new_list(agent, previous_agent, n)

    def new_list(self, agent, previous_agent, n):
        return list(set(self.G.nodes[agent][f'{n}_next_step_knowledge']) | set(self.G.nodes[agent][f'{n}']) | set(self.G.nodes[previous_agent][f'{n}']))

    def update_knowledge(self, agent):
        for n in range(self.degree_of_shared_knowledge):

            self.G.nodes[agent][f'{n}'] = list(set(self.G.nodes[agent][f'{n}']) | set(self.G.nodes[agent][f'{n}_next_step_knowledge']))

            if set(self.G.nodes[agent][f'{n}']) == set(list(self.G.nodes)):
                self.G.nodes[agent][f'{n}_knows'] = True

    '''
    Spread rumor to all neighboring agents
    '''

    def spread_rumor_to_all_neighbours(self):
        agent_that_know = [x for x, y in self.G.nodes(data=True) if y['rumor_is_known']]

        updateable_agents = []

        for knowledgeable_agent in agent_that_know:
            for agent in self.G.neighbors(knowledgeable_agent):
                self.spread_rumor_to_single_agent2(agent, knowledgeable_agent)
                updateable_agents.append(agent)
        
        updateable_agents = list(set(updateable_agents))
        for agent in updateable_agents:
            self.update_knowledge(agent)

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

    def update(self, degree_of_shared_knowledge):
        # keep track of knowledge
        self.rumor_is_known.append(self.count_knowledgeable('rumor_is_known'))

        for idx, n in enumerate(self.dynamic_E_known):
            n.append(self.count_knowledgeable(f'{idx}_knows'))

        # check if termination condition is met
        self.all_agents_know = True if self.count_knowledgeable(
            f'{degree_of_shared_knowledge - 1}_knows') == self.number_of_agents else False
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
        for idx, n in enumerate(self.dynamic_E_known):
            plt.plot(n, label=f'{idx}_knowledgeable')

        plt.legend()
        plt.show()


'''
Simulate rumor spreading
'''


def simulate(agents, connectivity, degree_of_shared_knowledge):
    random = np.random.randint(agents)

    G = Graph(agents, connectivity, degree_of_shared_knowledge)
    G.spread_rumor_to_first_agent(random)

    while not G.all_agents_know:
        # G.draw_graph()
        G.update(degree_of_shared_knowledge)
    G.plot_data()


def main():
    args = parser.parse_args()
    experiment_size = 1 # 3
    # agents = [20, 40, 80]
    # connectivity = [2, 10, 20]
    # degree_of_shared_knowledge = [2, 4, 10]
    agents = [5]
    connectivity = [5]
    degree_of_shared_knowledge = [10]


    for experiment in range(experiment_size):
        simulate(agents[experiment], connectivity[experiment], degree_of_shared_knowledge[experiment])

    # simulate(args.agents, args.connectivity, args.degree_of_shared_knowledge)


if __name__ == '__main__':
    main()
