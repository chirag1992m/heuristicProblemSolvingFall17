import math
import networkx as nx
import numpy as np

from gym.envs.board_game.connect_four import ConnectFourEnv


def get_height(state):
    height = np.zeros(7)
    for i in range(state.shape[-1]):
        height[i] = np.where(state[2][i])[0]
    return height


class StateNodeInfo:
    EXPLORATION_CONSTANT = 0.9

    def __init__(self):
        self.visit_count = 0
        self.value = 0
        self.prior_prob = 0
        self.parent_visit_count = 0

    def get_mean_value(self):
        if self.visit_count > 0:
            return self.value / float(self.visit_count)
        return 0.

    def get_value(self):
        return self.value

    def get_visit_count(self):
        return self.visit_count

    def add_visit_count(self, count):
        self.visit_count += count

    def add_value(self, value):
        self.value += value

    def set_prior(self, p):
        self.prior_prob = p

    def set_parent_visit(self, c):
        self.parent_visit_count = c

    def get_uncertainty(self):
        return (StateNodeInfo.EXPLORATION_CONSTANT
                * self.prior_prob
                * (math.sqrt(self.parent_visit_count) / (1 + self.visit_count)))

    def get_confidence(self):
        return self.get_mean_value() + self.get_uncertainty()

    def __str__(self):
        return "Node: N: {}, W: {}, Q {}, P {}, U {}, C {}".format(self.visit_count,
                                                                   self.value,
                                                                   self.get_mean_value(),
                                                                   self.prior_prob,
                                                                   self.get_uncertainty(),
                                                                   self.get_confidence())

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def pack_state(state):
        hash_val = 0
        position_val = 1
        for i in range(3):
            for j in range(3):
                if state[2][i][j] == 0:
                    if state[0][i][j]:
                        hash_val += position_val * 1
                    else:
                        hash_val += position_val * 2
                position_val *= 3
        return hash_val

    # @staticmethod
    # def unpack_state(num):
    #     state = np.zeros((3, 3, 3))
    #     state[2, :] = 1
    #     current_pos = 0
    #     while num > 0:
    #         rem = num % 3
    #         if rem == 1:
    #             coordinate = TicTacToeEnv.action_to_coordinate(current_pos, 3)
    #             state[0][coordinate[0]][coordinate[1]] = 1
    #             state[2][coordinate[0]][coordinate[1]] = 0
    #         elif rem == 2:
    #             coordinate = TicTacToeEnv.action_to_coordinate(current_pos, 3)
    #             state[1][coordinate[0]][coordinate[1]] = 1
    #             state[2][coordinate[0]][coordinate[1]] = 0
    #         num = num // 3
    #         current_pos += 1
    #     return state


class MoveEdgeInfo:
    def __init__(self, action):
        self.action = action
        self.visit_count = 0
        self.action_value = 0

    def get_action(self):
        return self.action

    def get_value(self):
        return self.action_value

    def get_visit_count(self):
        return self.visit_count

    def add_game(self, value, count=1):
        self.visit_count += count
        self.action_value += value

    def reset(self):
        self.visit_count = 0
        self.action_value = 0

    def __str__(self):
        return "Edge: a: {}, N {}, W {}".format(self.action, self.visit_count, self.action_value)

    def __repr__(self):
        return self.__str__()


class MCTSConnectFour:
    def __init__(self, S_0, current_player, agent, simulations=50,
                 temperature=1., temperature_decay=0.9):
        self.root_state = S_0.copy()
        self.current_state = self.root_state.copy()
        self.agent = agent
        self.simulations = simulations
        self.current_player = current_player
        self.temperature = temperature
        self.temperature_decay = temperature_decay
        self.tree = nx.DiGraph()

        self.build_mct()

    def build_mct(self):
        root = StateNodeInfo.pack_state(self.current_state)
        if root not in self.tree.nodes:
            self.tree.add_node(root,
                               node_info=StateNodeInfo())
        current_state = self.current_state.copy()
        possible_actions = ConnectFourEnv.get_possible_actions(self.current_state)
        for action in possible_actions:
            new_state = current_state.copy()
            height = get_height(new_state)
            ConnectFourEnv.make_move(new_state, height, action, self.current_player)
            self.tree.add_node(StateNodeInfo.pack_state(new_state),
                               node_info=StateNodeInfo())
            self.tree.add_edge(root,
                               StateNodeInfo.pack_state(new_state),
                               edge_info=MoveEdgeInfo(action))

    def move_to_child_with_action(self, action_taken):
        # Remove the MCTS tree not in use anymore
        nodes_to_remove = []
        current_node = StateNodeInfo.pack_state(self.current_state)
        for child in self.tree.successors(current_node):
            if self.tree.edges[(current_node, child)]['edge_info'].get_action() != action_taken:
                nodes_to_remove.append(child)
        self.tree.remove_nodes_from(nodes_to_remove)

        # Move to the node where the action is taken
        height = get_height(self.current_state)
        ConnectFourEnv.make_move(self.current_state, height, action_taken, self.current_player)
        self.current_player = 1 - self.current_player

        current_node = StateNodeInfo.pack_state(self.current_state)
        current_state = self.current_state.copy()
        possible_actions = ConnectFourEnv.get_possible_actions(self.current_state)
        for action in possible_actions:
            new_state = current_state.copy()
            height = get_height(new_state)
            ConnectFourEnv.make_move(new_state, height, action, self.current_player)
            new_state = StateNodeInfo.pack_state(new_state)
            self.tree.add_node(new_state,
                               node_info=StateNodeInfo())
            self.tree.add_edge(current_node,
                               new_state,
                               edge_info=MoveEdgeInfo(action))

        # Decrease the temperature
        self.temperature = self.temperature * self.temperature_decay

    def rollout(self, with_action):
        current_state = self.current_state.copy()

        chance = self.current_player
        height = get_height(current_state)
        ConnectFourEnv.make_move(current_state, height, with_action, self.current_player)
        while True:
            winner = ConnectFourEnv.get_winner(current_state)
            chance = 1 - chance
            if winner > 0:
                if winner == 3:
                    return 0.
                elif winner == self.current_player + 1:
                    return 1.
                else:
                    return -1
                # _, value = self.agent.get_non_torch_p_v(current_state, chance)
                # return value
            action = self.agent.get_action(current_state, chance)
            height = get_height(current_state)
            ConnectFourEnv.make_move(current_state, height, action, chance)

    def backup_trickle(self):
        # Backup
        current_node = StateNodeInfo.pack_state(self.current_state)
        downstream_done = False
        while True:
            count_upstream = 0
            value_upstream = 0
            for child in self.tree.neighbors(current_node):
                count = self.tree.edges[(current_node, child)]['edge_info'].get_visit_count()
                count_upstream += count
                value = self.tree.edges[(current_node, child)]['edge_info'].get_value()
                value_upstream += value
                if not downstream_done:
                    self.tree.nodes[child]['node_info'].add_visit_count(count)
                    self.tree.nodes[child]['node_info'].add_value(value)
                self.tree.edges[(current_node, child)]['edge_info'].reset()
            downstream_done = True
            self.tree.nodes[current_node]['node_info'].add_visit_count(count_upstream)
            self.tree.nodes[current_node]['node_info'].add_value(value_upstream)

            parent_nodes = list(self.tree.predecessors(current_node))
            if parent_nodes:
                assert len(parent_nodes) == 1, "Parent nodes more than 1!!"
                parent_node = parent_nodes[0]
                self.tree.edges[(parent_node, current_node)]['edge_info'].add_game(
                    value_upstream, count_upstream)
                current_node = parent_node
            else:
                break
        # Trickle
        current_node = StateNodeInfo.pack_state(self.root_state)
        while True:
            next_to_consider = []
            for child in self.tree.neighbors(current_node):
                self.tree.nodes[child]['node_info'].set_parent_visit(
                    self.tree.nodes[current_node]['node_info'].get_visit_count()
                )
                if list(self.tree.successors(child)):
                    next_to_consider.append(child)
            if next_to_consider:
                assert len(next_to_consider) == 1, "Successor nodes more than 1!!"
                current_node = next_to_consider[0]
            else:
                break

    def run_simulations(self, explore=0.25):
        P, _ = self.agent.get_non_torch_p_v(self.current_state, self.current_player)
        P = np.array(P) * (1 - explore) + (explore * np.random.dirichlet([0.03] * len(P)))
        parent = StateNodeInfo.pack_state(self.current_state)
        for child in self.tree.neighbors(parent):
            action = self.tree.edges[(parent, child)]['edge_info'].get_action()
            self.tree.nodes[child]['node_info'].set_prior(P[action])
            value = self.rollout(action)
            self.tree.edges[(parent, child)]['edge_info'].add_game(value)
        self.backup_trickle()

        for simulation in range(self.simulations):
            confidences = []
            children_keys = []
            for child in self.tree.neighbors(parent):
                confidences.append(self.tree.nodes[child]['node_info'].get_confidence())
                children_keys.append(child)
            child_to_explore = np.argmax(confidences)
            child_to_explore = children_keys[child_to_explore]
            action = self.tree.edges[(parent, child_to_explore)]['edge_info'].get_action()
            value = self.rollout(action)
            self.tree.edges[(parent, child_to_explore)]['edge_info'].add_game(value)
            self.backup_trickle()

    def get_simulated_policy_value(self):
        parent = StateNodeInfo.pack_state(self.current_state)
        action_visit = [0] * 9
        total_visit = 0
        for child in self.tree.neighbors(parent):
            action = self.tree.edges[(parent, child)]['edge_info'].get_action()
            count = self.tree.nodes[child]['node_info'].get_visit_count()
            count = math.pow(count, 1/self.temperature)
            total_visit += count
            action_visit[action] = count
        return (np.array(action_visit) / total_visit,
                self.tree.nodes[parent]['node_info'].get_mean_value())

    def print_tree(self):
        for node in self.tree.nodes:
            print(node, self.tree.nodes[node]['node_info'])

        for edge in self.tree.edges:
            print(edge, self.tree.edges[edge]['edge_info'])
