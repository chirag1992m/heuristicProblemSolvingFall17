import os
import pickle
import sys

from gym.envs.board_game.tic_tac_toe import TicTacToeEnv

paths = os.listdir('tic_tac_toe_train_data')
data_paths = []
for path in paths:
    if path.startswith('episode_'):
        data_paths.append(os.path.join('tic_tac_toe_train_data', path))

data = []
for data_path in data_paths:
    data.extend(pickle.load(open(data_path, 'rb')))

for x in data:
    state = x[0][0]
    chance = x[0][1]

    TicTacToeEnv.render_to_file(state, sys.stdout)
    print("Chance: {}, Value: {}, Pi: {}".format(chance, x[2], x[1]))
    _ = input("")
