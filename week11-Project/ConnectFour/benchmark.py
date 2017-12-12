"""
Script to benchmark
"""
import gym


def benchmark_agent(agent_1, agent_2, games=1000, randomize=False):
    if not randomize:
        agent_1.eval()
        agent_2.eval()
    env = gym.make('ConnectFour7x7-v0')
    agent_1_win, agent_2_win, draws = 0, 0, 0
    total_games = 0
    for i in range(games//2):
        total_games += 1
        obs = env.reset()
        # env.render()
        reward = None
        for move in range(9):
            if move % 2 == 0:
                action = agent_1.get_action(obs[1], 1)
                obs, reward, done, _ = env.step((1, action))
            else:
                action = agent_2.get_action(obs[0], 0)
                obs, reward, done, _ = env.step((0, action))
            # env.render()
            if all(done):
                break
        if reward[0] == 0.:     # Draw
            draws += 1
        elif reward[0] == -1:
            agent_1_win += 1
        else:
            agent_2_win += 1
    for i in range(games//2):
        total_games += 1
        obs = env.reset()
        # env.render()
        reward = None
        for move in range(9):
            if move % 2 == 0:
                action = agent_2.get_action(obs[1], 1)
                obs, reward, done, _ = env.step((1, action))
            else:
                action = agent_1.get_action(obs[0], 0)
                obs, reward, done, _ = env.step((0, action))
            # env.render()
            if all(done):
                break
        if reward[0] == 0.:     # Draw
            draws += 1
        elif reward[0] == -1:
            agent_2_win += 1
        else:
            agent_1_win += 1

    print("Benchmarking: Draws {}, {}: {}, {}: {}".format(
        draws/float(total_games),
        agent_1.get_name(), agent_1_win/float(total_games),
        agent_2.get_name(), agent_2_win/float(total_games)
    ))
    return draws/float(total_games), agent_1_win/float(total_games), agent_2_win/float(total_games)
