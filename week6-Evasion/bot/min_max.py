import argparse
import itertools
import numpy as np
import random

from .base_bot import BaseBot
from .game_info import GameInfo


class MinMaxBot(BaseBot):

    def __init__(self, host, port, name, visualize=False):
        super().__init__(host=host, port=port, name=name, visualize=visualize)

    def move_hunter(self):
        wall = random.randint(0, 4)
        to_delete = []
        for wall_idx in range(len(self.game.walls)):
            if random.random() < .1:
                to_delete.append(wall_idx)
        return wall, to_delete

    @staticmethod
    def score(game_state):
        hunter_pos = np.where(game_state['grid'] == 2)
        prey_pos = np.where(game_state['grid'] == 3)

        hunter_pos_x, hunter_pos_y = hunter_pos[0][0], hunter_pos[1][0]
        prey_pos_x, prey_pos_y = prey_pos[0][0], prey_pos[1][0]

        return (hunter_pos_x - prey_pos_x)**2 + (hunter_pos_y - prey_pos_y)**2

    def min_max_prey(self, game_state, depth, max_depth):
        if depth == max_depth:
            return (0, 0), self.score(game_state)

        if depth % 2 == 1:  # Only hunter can move. Hunter will Minimize
            scores_and_moves = [self.min_max_prey(GameInfo.simulate_move(game_state,
                                                                         hunter_move,
                                                                         (0, 0)),
                                                  depth=depth+1,
                                                  max_depth=max_depth)
                                for hunter_move in range(5)]
            _, score = min(scores_and_moves, key=lambda x: x[1])
            return (0, 0), score
        best_score = None
        best_move = None
        for prey_move in itertools.product([-1, 0, 1], [-1, 0, 1]):
            scores_and_moves = [self.min_max_prey(GameInfo.simulate_move(game_state,
                                                                         hunter_move,
                                                                         prey_move),
                                                  depth=depth+1,
                                                  max_depth=max_depth)
                                for hunter_move in range(5)]
            mean_score = np.mean([x[1] for x in scores_and_moves])
            if best_score is None or mean_score > best_score:
                best_score = mean_score
                best_move = prey_move
        return best_move, best_score

    def move_prey(self):
        # We are not allowed to move on Even ticks, sending
        # placeholder values
        if self.game.tick and self.game.tick % 2 == 0:
            return 0, 0
        move, _ = self.min_max_prey({'grid': self.game.grid,
                                     'hunter_velocity': self.game.hunter_velocity},
                                    depth=0, max_depth=2)
        print(move)
        return move


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', default='127.0.0.1', type=str)
    parser.add_argument('--port', default=9001, type=int)
    parser.add_argument('--name', default='chirag-ojas', type=str)
    parser.add_argument('--viz', default=False, action='store_true')
    args = parser.parse_args()

    client = MinMaxBot(args.ip, args.port, args.name, visualize=args.viz)
    client.start()
    client.done()
