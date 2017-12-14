import numpy as np

import torch
from torch import nn
from torch.autograd import Variable
from torch.nn import functional


class AlphaZeroConnectFour(nn.Module):
    def __init__(self):
        super(AlphaZeroConnectFour, self).__init__()

        in_channel = 3
        self.input_nodes = 16 + 1
        action_output = 7
        value_output = 1
        self.layers = nn.Sequential(
            nn.Conv2d(in_channels=in_channel, out_channels=8, kernel_size=4,
                      stride=1, padding=0),
            nn.ReLU(),
            nn.Conv2d(in_channels=8, out_channels=16, kernel_size=4,
                      stride=1, padding=0),
            nn.ReLU()
        )
        self.P = nn.Linear(self.input_nodes, action_output)
        self.V = nn.Linear(self.input_nodes, value_output)

        self.P_squash = functional.softmax
        self.V_squash = functional.tanh

    def forward(self, x, chance, mask):
        intermediate = self.layers(x)
        intermediate = torch.cat((intermediate.view(-1, self.input_nodes - 1), chance), dim=1)

        P = self.P_squash(self.P(intermediate))
        P = P * mask
        y = torch.sum(P, dim=1)
        y = torch.unsqueeze(y, dim=1)
        P = P / y
        V = self.V_squash(self.V(intermediate))

        return P, V


def loss_function(P, V, pi, z):
    value_loss = functional.mse_loss(torch.squeeze(V), z)
    policy_loss = functional.binary_cross_entropy(torch.squeeze(P), pi)

    return value_loss + policy_loss


def get_tensor_from_state(state, chance, variable=True):
    x = torch.from_numpy(state.astype(np.float32))
    x = torch.unsqueeze(x, dim=0)
    if chance == 0:
        chance = -1.
    y = torch.from_numpy(np.array([chance], dtype=np.float32))
    y = torch.unsqueeze(y, dim=0)
    return (Variable(x), Variable(y)) if variable else (x, y)


def get_possible_action_mask(possible_actions, variable=True):
    mask = torch.zeros(7)
    for move in possible_actions:
        mask[move] = 1.0
    return Variable(mask) if variable else mask
