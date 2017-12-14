import numpy as np

import torch
from torch import nn
from torch.autograd import Variable
from torch.nn import functional


class AlphaZeroTicTacToe(nn.Module):
    def __init__(self):
        super(AlphaZeroTicTacToe, self).__init__()

        input_nodes = 3 * 3 * 3 + 1
        action_output = 9
        value_output = 1
        hidden_outputs = 32
        self.layers = nn.Sequential(
            nn.Linear(input_nodes, hidden_outputs),
            nn.ReLU(),
            nn.Linear(hidden_outputs, hidden_outputs),
            nn.ReLU()
        )
        self.P = nn.Linear(hidden_outputs, action_output)
        self.V = nn.Linear(hidden_outputs, value_output)

        self.P_squash = functional.softmax
        self.V_squash = functional.tanh

    def forward(self, x, mask):
        intermediate = self.layers(x)

        P = self.P_squash(self.P(intermediate))
        P = P * mask
        y = torch.sum(P, dim=2).clamp(min=1e-12)
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
    x = x.view(-1)
    if chance == 0:
        chance = -1.
    x = torch.cat((x, torch.FloatTensor([chance])))
    x = x.view(1, -1)
    return Variable(x) if variable else x


def get_possible_action_mask(possible_actions, variable=True):
    mask = torch.zeros(1, 9)
    for move in possible_actions:
        mask[0][move] = 1.0
    return Variable(mask) if variable else mask
