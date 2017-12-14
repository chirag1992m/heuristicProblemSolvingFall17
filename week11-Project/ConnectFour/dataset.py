import numpy as np
import pickle

from gym.envs.board_game.connect_four import ConnectFourEnv

import torch
from torch.utils.data import Dataset

from .model import get_tensor_from_state, get_possible_action_mask


class GamePlayData(Dataset):
    def __init__(self, data_paths):
        self.data = []
        for data_path in data_paths:
            self.data.extend(pickle.load(open(data_path, 'rb')))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        data = self.data[idx]
        state = data[0][0]
        chance = data[0][1]

        pi = data[1]
        z = data[2]

        possible_actions = ConnectFourEnv.get_possible_actions(state)
        x, y = get_tensor_from_state(state, chance, variable=False)
        x = torch.squeeze(x, dim=0)
        y = torch.squeeze(y, dim=0)
        return {
            'inp_state': x,
            'inp_chance': y,
            'mask': get_possible_action_mask(possible_actions, variable=False),
            'PI': np.array(pi, dtype=np.float32),
            'Z': np.array([z], dtype=np.float32)
        }
