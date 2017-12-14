"""
Code to train the Connect-Four Self-Play agent as given in

Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm
(AlphaZero) https://arxiv.org/abs/1712.01815

The model and loss function is given in model.py. The training loop is generalised to
the following loop of:

1. Start from Randomly Initialised Model
2. Generate Training Data by Self-Play Game Simulations using
    Monte-Carlo Tree-Search (MCTS)
3. Train the model on the generated data
4. Evaluate/Benchmark the new model with the best model available
5. Choose the best model and checkpoint it
6. Repeat from step-2. The training stops when the model stops
    improving.
"""
import numpy as np
import os
import pickle
import random
import shutil

import gym

import torch
from torch.utils.data import DataLoader
from torch import optim
from torch.autograd import Variable

from .model import AlphaZeroConnectFour, loss_function
from .agents import SelfPlayRLAgent, RandomPlayer
from .monte_carlo_tree_search import MCTSConnectFour
from .dataset import GamePlayData
from .benchmark import benchmark_agent

# Parameters
learning_rate = 0.001
weight_decay = 0.0001
episodes = 100
epochs = 500
win_ratio = 55
training_games = 50
mcts_simulations = 50
batch_size = 64
epoch_logging = 50
temperature = 1.
temperature_expand = 1.15
improvement_patience = 10
win_ratio_factor = .8
win_ratio_min = 10
early_stopping_patience = 50
randomize_eval = True
best_random_ratio = 0.0
cuda = True and torch.cuda.is_available()

# Set Seeds for Reproducibility
torch.manual_seed(42)
np.random.seed(42)
random.seed(42)
if cuda:
    torch.cuda.manual_seed(42)

# Initialize variables
current_model = AlphaZeroConnectFour()
best_model = AlphaZeroConnectFour()
best_model.load_state_dict(current_model.state_dict())

optimizer = optim.Adam(current_model.parameters(),
                       lr=learning_rate,
                       weight_decay=weight_decay)

training_data = []


def generate_training_data(agent, data_path, n_games=training_games):
    print("Generating Training data...")
    global training_data
    env = gym.make('ConnectFour7x7-v0')
    for game in range(n_games):
        current_game_data = []
        obs = env.reset()
        chance = 1
        reward = [0., 0.]
        mcts = MCTSConnectFour(obs[chance], chance, agent, simulations=mcts_simulations,
                               temperature=temperature, temperature_expand=temperature_expand)
        while True:
            mcts.run_simulations()
            pi, z = mcts.get_simulated_policy_value()
            current_game_data.append(((obs[chance].copy(), chance),
                                      pi, z))
            action = np.random.choice(np.arange(7), p=pi)
            obs, reward, done, _ = env.step((chance, action))
            if all(done):
                current_game_data.append(((obs[chance].copy(), chance),
                                          [0.] * 7, reward[1 - chance]))
                current_game_data.append(((obs[chance].copy(), 1 - chance),
                                          [0.] * 7, reward[chance]))
                break
            chance = 1 - chance
            mcts.move_to_child_with_action(action)
        # for i, game_data in enumerate(current_game_data):
        #     training_data.append((
        #         game_data[0],
        #         game_data[1],
        #         reward[(i+1) % 2]
        #     ))
        training_data.extend(current_game_data)
    pickle.dump(training_data, open(data_path, 'wb'))
    print("Training data generated of length {} with agent {} and stored at {}".format(
        len(training_data),
        agent.get_name(),
        data_path))
    training_data = []


def train_model(dataset_path, path_to_save):
    dataset = GamePlayData(dataset_path)
    dataloader = DataLoader(dataset,
                            batch_size=batch_size,
                            shuffle=True)
    print("Training model with last {} data totalling {} data-point...".format(
        len(dataset_path),
        len(dataset)
    ))
    best_loss = None
    wait = 0
    epoch = 0
    for epoch in range(1, epochs+1):
        losses = []
        for batch_id, data in enumerate(dataloader):
            states, chances = Variable(data['inp_state']), Variable(data['inp_chance'])
            masks = Variable(data['mask'])
            P, V = current_model(states, chances, masks)
            PI, Z = Variable(data['PI']), Variable(data['Z'])
            loss = loss_function(P, V, PI, Z)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            losses.append(loss.data.numpy()[0])
        epoch_loss = np.mean(losses)
        if epoch % epoch_logging == 0:
            print("Epoch: {}, Loss: {}".format(epoch, epoch_loss))
        if best_loss is None or epoch_loss < best_loss - 1e-5:
            best_loss = epoch_loss
            wait = 0
        else:
            wait += 1
            if wait >= early_stopping_patience:
                print("Early stopping training...")
                break
    print("Training Complete for Epochs {} with best loss {}".format(epoch, best_loss))

    if os.path.exists(path_to_save):
        os.remove(path_to_save)
    torch.save({'model': current_model.state_dict()}, path_to_save)


def evaluate(agent_1, agent_2):
    print("Evaluating agent...")
    draw, win_1, win_2 = benchmark_agent(agent_1, agent_2, randomize=randomize_eval)
    if win_2 > 0:
        ratio = ((win_1 - win_2) * 100)/win_2
    else:
        ratio = float('inf')
    print("Evaluation complete with win ratio: {}".format(ratio))
    return ratio > win_ratio, ratio


TRAIN_DIR = 'connect_four_train_data'
BEST_MODEL_PATH = os.path.join(TRAIN_DIR, 'best_agent.pkl')
CURRENT_MODEL_PATH = os.path.join(TRAIN_DIR, 'current_agent.pkl')
if os.path.exists(TRAIN_DIR):
    shutil.rmtree(TRAIN_DIR)
os.mkdir(TRAIN_DIR)

torch.save({'model': best_model.state_dict()}, BEST_MODEL_PATH)
improve_patience = 0
for episode in range(1, episodes+1):
    best_agent = SelfPlayRLAgent(BEST_MODEL_PATH, "best_agent")
    best_agent.train()

    TRAINING_DATA_PATH = os.path.join(TRAIN_DIR, 'episode_{}.pkl'.format(episode))
    generate_training_data(best_agent, TRAINING_DATA_PATH)

    training_data_paths = []
    for i in range(improve_patience+1):
        training_data_paths.append(os.path.join(TRAIN_DIR, 'episode_{}.pkl'.format(episode - i)))
    train_model(training_data_paths, CURRENT_MODEL_PATH)

    current_agent = SelfPlayRLAgent(CURRENT_MODEL_PATH, "current_agent")
    better, _ = evaluate(current_agent, best_agent)
    print("Completed episode: {}".format(episode))

    _, _ = evaluate(current_agent, RandomPlayer())
    if better:
        improve_patience = 0
        win_ratio = max(win_ratio * win_ratio_factor, win_ratio_min)
        print("Found better agent...updating...")
        best_model.load_state_dict(current_model.state_dict())
        os.remove(BEST_MODEL_PATH)
        torch.save({'model': best_model.state_dict()}, BEST_MODEL_PATH)
    else:
        improve_patience += 1
        if improve_patience >= improvement_patience:
            print("No improvement since last episodes. Stopping training...")
            break
