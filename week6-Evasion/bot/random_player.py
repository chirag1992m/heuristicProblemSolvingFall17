import argparse
from base_bot import BaseBot
import random


class RandomBot(BaseBot):

    def __init__(self, host, port, name, visualize=False, seed=42):
        super().__init__(host=host, port=port, name=name, visualize=visualize)
        random.seed(seed)

    def move_hunter(self):
        wall = random.randint(0, 4)
        to_delete = []
        for wall_idx in range(len(self.game.walls)):
            if random.random() < .1:
                to_delete.append(wall_idx)
        return wall, to_delete

    def move_prey(self):
        x = random.randint(-1, 1)
        y = random.randint(-1, 1)
        return x, y


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', default='127.0.0.1', type=str)
    parser.add_argument('--port', default=9001, type=int)
    parser.add_argument('--name', default='chirag-ojas', type=str)
    parser.add_argument('--viz', default=False, action='store_true')
    parser.add_argument('--seed', default=42, type=int)
    args = parser.parse_args()

    client = RandomBot(args.ip, args.port, args.name, visualize=args.viz, seed=args.seed)
    client.start()
    client.done()
