"""
File containing the different agents. All agents inherit
the general Agent class returns name and action on calling
it's method.
"""
import sys
import numpy as np
import torch

from .model import AlphaZeroTicTacToe, get_possible_action_mask, get_tensor_from_state

from gym.utils import seeding
from gym.envs.board_game.tic_tac_toe import make_tic_tac_toe_random_policy
from gym.envs.board_game.tic_tac_toe import TicTacToeEnv


class Agent(object):
    def __init__(self):
        super(Agent, self).__init__()

    def get_action(self, state, chance):
        raise NotImplementedError("Agent action not implemented")

    def get_name(self):
        return "No Agent!"


class SelfPlayRLAgent(Agent):
    def __init__(self, filename, name=None, verbose=False, eval=False):
        super(SelfPlayRLAgent, self).__init__()
        checkpoint = torch.load(filename if filename is not None else SelfPlayRLAgent.filename())
        self.model = AlphaZeroTicTacToe()
        self.model.load_state_dict(checkpoint['model'])
        self.model.eval()
        self.name = 'Self_Play'
        if name is not None:
            self.name = name
        self.verbose = verbose
        self.eval = eval

    def get_p_v(self, state, chance):
        possible_moves = TicTacToeEnv.get_possible_actions(state)
        x = get_tensor_from_state(state, chance)
        mask = get_possible_action_mask(possible_moves)
        return self.model(x, mask)

    def get_non_torch_p_v(self, state, chance):
        P, V = self.get_p_v(state, chance)
        return P.data.numpy()[0], V.data.numpy()[0][0]

    def get_action_sampled(self, state, chance):
        P, V = self.get_p_v(state, chance)
        if self.verbose:
            print(P, V)
        return torch.multinomial(P[0], num_samples=1)[0]

    def get_action_value_maximizer(self, state, chance):
        possible_actions = TicTacToeEnv.get_possible_actions(state)
        if not possible_actions:
            return None
        values = [-1.1] * 9
        for action in possible_actions:
            current_state = state.copy()
            TicTacToeEnv.make_move(current_state, action, chance)
            _, value = self.get_non_torch_p_v(current_state, 1 - chance)
            values[action] = value
        action_to_take = np.argmax(values)
        if self.verbose:
            print("Next Values: ", values, action_to_take)
        return action_to_take

    def get_action(self, state, chance):
        if self.eval:
            return self.get_action_value_maximizer(state, chance)
        else:
            return self.get_action_sampled(state, chance).data.numpy()[0]

    def get_name(self):
        return self.name

    @staticmethod
    def filename():
        return "TicTacToeAgent.pkl"


class RandomPlayer(Agent):
    def __init__(self):
        super(RandomPlayer, self).__init__()
        np_random, _ = seeding.np_random(42)
        self.player = make_tic_tac_toe_random_policy(np_random)
        self.name = "Random"

    def get_action(self, state, chance):
        return self.player(state)

    def get_name(self):
        return self.name


class HumanPlayer(Agent):
    def __init__(self):
        super(HumanPlayer, self).__init__()
        self.name = "Human"

    def get_action(self, state, chance):
        action = int(input("Human, make your move {}: ".format(chance)))
        return action - 1

    def get_name(self):
        return self.name
