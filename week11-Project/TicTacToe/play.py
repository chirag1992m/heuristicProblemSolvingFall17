import argparse
import gym

from .agents import HumanPlayer, RandomPlayer, SelfPlayRLAgent

parser = argparse.ArgumentParser("Play Tic-Tac-Toe between two players")

parser.add_argument("--p1", choices=['self_play', 'random', 'human'], default='self_play')
parser.add_argument("--p2", choices=['self_play', 'random', 'human'], default='human')

args = parser.parse_args()

env = gym.make('TicTacToe3x3-v0')

cross_player = None
if args.p1 == 'self_play':
    cross_player = SelfPlayRLAgent('tic_tac_toe_train_data/best_agent.pkl',
                                   verbose=True)
elif args.p1 == 'human':
    cross_player = HumanPlayer()
elif args.p1 == 'random':
    cross_player = RandomPlayer()

naught_player = None
if args.p2 == 'self_play':
    naught_player = SelfPlayRLAgent('tic_tac_toe_train_data/best_agent.pkl',
                                    verbose=True)
elif args.p2 == 'human':
    naught_player = HumanPlayer()
elif args.p2 == 'random':
    naught_player = RandomPlayer()

cross_player.eval()
naught_player.eval()

obs = env.reset()
while True:
    action = cross_player.get_action(obs[1], 1)
    obs, reward, done, _ = env.step((1, action))
    env.render()
    print(reward)
    if all(done):
        break
    action = naught_player.get_action(obs[0], 0)
    obs, reward, done, _ = env.step((0, action))
    env.render()
    print(reward)
    if all(done):
        break

if reward[0] == 0.:
    print("This was draw.")
elif reward[0] == -1.:
    print("Player {} win!".format(cross_player.get_name()))
else:
    print("Player {} win!".format(naught_player.get_name()))

print("Switching sides now!")
obs = env.reset()
while True:
    action = naught_player.get_action(obs[1], 1)
    obs, reward, done, _ = env.step((1, action))
    env.render()
    print(reward)
    if all(done):
        break
    action = cross_player.get_action(obs[0], 0)
    obs, reward, done, _ = env.step((0, action))
    env.render()
    print(reward)
    if all(done):
        break

if reward[0] == 0.:
    print("This was draw.")
elif reward[0] == -1.:
    print("Player {} win!".format(naught_player.get_name()))
else:
    print("Player {} win!".format(cross_player.get_name()))
