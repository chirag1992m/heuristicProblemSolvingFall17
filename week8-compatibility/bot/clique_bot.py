import argparse
from .game_client import GameClient
import random
import networkx as nx
import matplotlib.pyplot as plt
import time
import math


class CliqueBot(GameClient):
    def __init__(self,
                 server_address,
                 server_port,
                 player_role,
                 player_name,
                 game_params):
        super(CliqueBot, self).__init__(server_address,
                                        server_port,
                                        player_role,
                                        player_name,
                                        game_params)
        self.graph = nx.Graph()
        random.seed(42)
        self.nodes_per_package = None

    def create_empty_graph(self):
        self.graph.clear()
        nodes = [str((i // self.parameters['packages']) + 1)
                 + '_'
                 + str((i % self.parameters['packages']) + 1)
                 for i in range(self.parameters['packages'] * self.parameters['versions'])]
        self.graph.add_nodes_from(nodes)
        print("Graph has {} vertices.".format(self.graph.number_of_nodes()))
        # nx.draw(self.graph)
        # plt.show()

    def add_edges_from_pairs(self):
        for pair in self.pairs:
            if pair[0][0] == pair[1][0]:    # Edges in the same set of
                continue
            self.graph.add_edge(str(pair[0][0]) + '_' + str(pair[0][1]),
                                str(pair[1][0]) + '_' + str(pair[1][1]))
        # nx.draw(self.graph)
        # plt.show()

    def poser(self):
        self.create_empty_graph()
        n = self.parameters['packages']
        m = self.parameters['versions']
        pairs = []
        configs = []
        for i in range(n):
            v = random.randint(int(m / 2 - math.sqrt(m)), int(m / 2 + math.sqrt(m)))
            if v < 1:
                v = m // 2
            if v > m:
                v = m // 2
            configs.append(v)

        # our max clique added to graph
        pairs_added = 0
        pairs_allowed = self.parameters['compatibilities']
        pairs_left = pairs_allowed
        for pack1 in range(1, n + 1):
            for pack2 in range(pack1 + 1, n + 1):
                if pack1 == pack2:
                    continue
                pairs.append(((pack1, configs[pack1 - 1]), (pack2, configs[pack2 - 1])))
                pairs_added += 1

        pairs_left -= pairs_added
        pairs_clique = pairs_added
        # add more cliques below this clique
        below = pairs_left / 2
        while below > 0:
            temp_clique = []
            for i in range(n):
                v = random.randint(1, configs[i])
                temp_clique.append(v)
            for pack in range(1, n + 1):
                for pack2 in range(1, n + 1):
                    if pack == pack2:
                        continue
                    pairs.append(((pack1, temp_clique[pack1 - 1]), (pack2, temp_clique[pack2 - 1])))
                    pairs_added += 1
                    pairs_left -= 1
                    below -= 1
                    if below <= 0:
                        break

        # add randomly edges above our clique
        while pairs_left > 0:
            temp1 = []
            temp2 = []

            for i in range(n):
                v = random.randint(configs[i], m)
                temp1.append(v)
                v2 = v
                while (v2 == v):
                    v2 = random.randint(configs[i], m)
                temp2.append(v2)

            for pack in range(1, n + 1):
                if pairs_left <= 0:
                    break
                for pack2 in range(1, n + 1):
                    if pairs_left <= 0:
                        break
                    if (pack == pack2):
                        continue
                    pairs.append(((pack1, temp1[pack1 - 1]), (pack2, temp2[pack2 - 1])))
                    pairs_added += 1
                    pairs_left -= 1

        while pairs_left > 0:
            p1 = random.randint(1, n)
            p2 = p1
            while p2 == p1:
                p2 = random.randint(1, n)
            v1 = random.randint(1, m)
            v2 = random.randint(1, m)
            pairs.append(((p1, v1), (p2, v2)))
            pairs_added += 1
            pairs_left -= 1
            if pairs_left <= 0:
                break

        configs = [configs]
        print(len(pairs), pairs_left)
        return pairs, configs

    def remove_vertices_with_less_edges(self):
        while True:
            nodes_to_remove = []
            for node in self.graph.nodes:
                if self.graph.degree(node) < self.parameters['packages'] - 1:
                    # Remove a vertex if it's degree is less than
                    # the number of packages
                    # as it wouldn't ever be a part of clique of size
                    # self.parameters['packages'] - 1
                    nodes_to_remove.append(node)
            for node in nodes_to_remove:
                self.graph.remove_node(node)
            if len(nodes_to_remove) == 0:
                break
        print("Graph has {} vertices left "
              "after removing vertices with small degree.".format(self.graph.number_of_nodes()))
        # nx.draw(self.graph)
        # plt.show()

    def sample_nodes(self):
        nodes_per_package = dict()
        for package in range(1, self.parameters['packages'] + 1):
            nodes_per_package[package] = []
        for node in self.graph.nodes:
            package = int(node.split('_')[0])
            nodes_per_package[package].append(node)
        print("nodes per package: ", nodes_per_package)
        self.nodes_per_package = nodes_per_package
        first, last = 1, self.parameters['packages']
        for version in sorted(self.nodes_per_package[first],
                              key=lambda x: int(x.split('_')[1]),
                              reverse=True):
            visited = [version]
            stack = [iter(set(self.graph.neighbors(version)).intersection(
                self.nodes_per_package[first+1]))]
            while stack:
                children = iter(stack[-1])
                child = next(children, None)
                if child is None:
                    stack.pop()
                    visited.pop()
                elif len(visited) < self.parameters['packages'] - 1:
                    visited.append(child)
                    package = int(child.split('_')[0])
                    stack.append(sorted(list(set(self.graph.neighbors(version)).intersection(
                        self.nodes_per_package[package+1])),
                                        key=lambda x: int(x.split('_')[1]),
                                        reverse=True))
                else:
                    if child not in self.nodes_per_package[last]:
                        "WTF!"
                        stack.pop()
                        visited.pop()
                    yield visited + [child]
                    stack.pop()
                    visited.pop()

    def find_k_cliques(self):
        edges_required = (self.parameters['packages'] * (self.parameters['packages'] - 1))//2
        for sampled_nodes in self.sample_nodes():
            if self.graph.subgraph(sampled_nodes).number_of_edges() == edges_required:
                yield sampled_nodes

    def remove_vertices_with_fake_edges(self):
        while True:
            nodes_to_remove = []
            for node in self.graph.nodes:
                neighbor_set = set()
                for neighbor in self.graph.neighbors(node):
                    package = int(neighbor.split('_')[0])
                    neighbor_set.add(package)
                if len(neighbor_set) < self.parameters['packages'] - 1:
                    nodes_to_remove.append(node)
            for node in nodes_to_remove:
                self.graph.remove_node(node)
            if len(nodes_to_remove) == 0:
                break
        print("Graph has {} vertices left after removing "
              "vertices with fake edges.".format(self.graph.number_of_nodes()))

    def solver(self):
        now = time.time()
        self.create_empty_graph()
        self.add_edges_from_pairs()
        self.remove_vertices_with_less_edges()
        self.remove_vertices_with_fake_edges()
        print("Graph with {} vertices and {} edges remain".format(self.graph.number_of_nodes(),
                                                                  self.graph.number_of_edges()))
        configs = []
        for clique in self.find_k_cliques():
            config = []
            for node in sorted(clique, key=lambda x: int(x.split('_')[0])):
                version = int(node.split('_')[1])
                config.append(version)
            configs.append(config)
            if time.time() - now > 100:
                print("Time ran out!")
                break
        return self.choose_best_config(configs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost', type=str)
    parser.add_argument('--port', default=34567, type=int)
    parser.add_argument('--player', default='both', type=str)
    parser.add_argument('--problem-id', default=None, type=str)
    parser.add_argument('--game-id', default=None, type=int)
    parser.add_argument('--access-code', default=None, type=int)
    parser.add_argument('--packages', default=20, type=int)
    parser.add_argument('--versions', default=40, type=int)
    parser.add_argument('--pairs', default=10000, type=int)

    args = parser.parse_args()
    print(args)
    if args.game_id is not None and args.access_code:
        client = CliqueBot(args.host, args.port,
                           args.player, 'CO',
                           {'game_id': args.game_id,
                            'access_code': args.access_code,
                            'problem_id': args.problem_id})
        client.play()
    elif args.player == 'both':
        client = CliqueBot(args.host, args.port,
                           'poser', 'CO',
                           {'packages': args.packages,
                            'versions': args.versions,
                            'pairs': args.pairs})
        client.play()
        client.play_as_solver()
    else:
        client = CliqueBot(args.host, args.port,
                           args.player, 'CO',
                           {'packages': args.packages,
                            'versions': args.versions,
                            'pairs': args.pairs})
        client.play()
