import argparse
from client import Client
from cluster_bot import ClusterBot
import multiprocessing
import time


parser = argparse.ArgumentParser()
parser.add_argument("bot1", type=str,
                    choices=['random', 'cluster'])
parser.add_argument("bot2", type=str,
                    choices=['random', 'cluster'])
parser.add_argument('--times', default=5, type=int)
parser.add_argument('--ip', default='127.0.0.1', type=str)
parser.add_argument('--port', default=8000, type=int)


def get_bot(bot_type, arg):
    if bot_type == 'random':
        return Client(arg.ip, arg.port, bot_type)
    elif bot_type == 'cluster':
        return ClusterBot(arg.ip, arg.port, bot_type)


def run_bot1(arg, counter):
    bot = get_bot(arg.bot1, arg)
    bot.start()
    if bot.winner == 1:
        counter.value += 1


def run_bot2(arg, counter):
    bot = get_bot(arg.bot2, arg)
    bot.start()
    if bot.winner == 2:
        counter.value += 1


if __name__ == "__main__":
    args = parser.parse_args()
    winner_count_1 = multiprocessing.Value('i', 0)
    winner_count_2 = multiprocessing.Value('i', 0)
    for _ in range(args.times):
        jobs = []
        p1 = multiprocessing.Process(name='player_1', target=run_bot1,
                                     args=(args, winner_count_1,))
        jobs.append(p1)
        p1.start()
        time.sleep(1)
        p2 = multiprocessing.Process(name='player_2', target=run_bot2,
                                     args=(args, winner_count_2,))
        jobs.append(p2)
        p2.start()
        for job in jobs:
            job.join()
        time.sleep(5.0)

    print("Player {} win count: {}".format(args.bot1, winner_count_1.value))
    print("Player {} win count: {}".format(args.bot2, winner_count_2.value))
