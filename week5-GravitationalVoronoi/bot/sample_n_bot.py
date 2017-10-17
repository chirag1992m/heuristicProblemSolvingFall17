import random
import argparse
import numpy as np
import itertools
from client import Client


class SampleNBot(Client):

    def __init__(self, host, port, name):
        super().__init__(host, port, name)
        self.N = 100

        #To keep track of score
        self.last_move_updated = 0
        self.game_grid = np.zeros((self.grid_size, self.grid_size), dtype=np.int)
        self.score_grid = np.zeros((self.grid_size, self.grid_size), dtype=np.int)
        self.scores = np.zeros(self.num_players, dtype=np.float32)
        self.pull = np.zeros((self.num_players, self.grid_size, self.grid_size), dtype=np.float32)

        self.row_numbers = np.zeros((self.grid_size, self.grid_size), dtype=np.float32)
        for i in range(self.grid_size):
            self.row_numbers[i] = self.row_numbers[i] + i
        self.col_numbers = np.transpose(self.row_numbers)

    def sample_n_valid_points(self):
        n_sampled_points = []
        for i in range(self.N):
            while True:
                row = random.randint(0, self.grid_size - 1)
                col = random.randint(0, self.grid_size - 1)
                if self._Client__is_valid_move(row, col):
                    break
            n_sampled_points.append((row, col))

        return n_sampled_points

    def compute_pull(self, row, col):
        squared_distance_matrix = np.square(self.row_numbers - row) + np.square(
            self.col_numbers - col)
        squared_distance_matrix[row][col] = 0.1e-30
        return np.reciprocal(squared_distance_matrix)

    def get_close_pulls(self, pull):
        equal_pull = np.zeros((self.grid_size, self.grid_size), dtype=np.bool)
        for p1, p2 in itertools.combinations(range(self.num_players), 2):
            equal_pull = np.logical_or(equal_pull,
                                       np.isclose(pull[p1], pull[p2],
                                                  rtol=0, atol=1e-15))
        return equal_pull

    def update_player_score(self, move):
        row, col, player = move
        player -= 1
        self.pull[player] += self.compute_pull(row, col)

        self.score_grid = np.argmax(self.pull, axis=0) + 1

        equal_pull = self.get_close_pulls(self.pull)
        self.score_grid[equal_pull] = 0

        for i in range(self.num_players):
            self.scores[i] = np.sum(self.score_grid == (i + 1))

    def update_scores(self):
        for i in range(self.last_move_updated, len(self.moves)):
            self.update_player_score(self.moves[i])
        self.last_move_updated = len(self.moves)

    def pseudo_update_scores(self, row, col):
        player = self.player_number
        player -= 1
        pull = np.copy(self.pull)
        pull[player] += self.compute_pull(row, col)

        score_grid = np.argmax(pull, axis=0) + 1

        equal_pull = self.get_close_pulls(pull)
        score_grid[equal_pull] = 0

        scores = np.copy(self.scores)
        for i in range(self.num_players):
            scores[i] = np.sum(score_grid == (i + 1))
        return scores[player]

    def get_point_with_best_score(self, points):
        self.update_scores()
        best_score = -1
        best_point = points[0]
        for point in points:
            score = self.pseudo_update_scores(point[0], point[1])
            if score > best_score:
                best_score = score
                best_point = point
        return best_point

    def get_move(self):
        sampled_points = self.sample_n_valid_points()
        return self.get_point_with_best_score(sampled_points)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', default='127.0.0.1', type=str)
    parser.add_argument('--port', default=8000, type=int)
    parser.add_argument('--name', default='chirag-ojas', type=str)
    args = parser.parse_args()

    client = SampleNBot(args.ip, args.port, args.name)
    client.start()
    print("Game over! Winner: {}".format(client.winner))
