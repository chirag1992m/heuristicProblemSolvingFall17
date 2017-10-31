import argparse
from hopcroftkarp import HopcroftKarp
import random
import numpy
import time

from .base_bot import BaseBot


class SamplingBot(BaseBot):
    def __init__(self, host, port, name, role='choreographer'):
        super(SamplingBot, self).__init__(host, port, name, role)

    def match(self, stars, dancers):
        l = 0
        h = 1000000
        for i in range(30):
            m = (l + h) / 2
            graph = {}
            for dancer in dancers:
                for star in stars:
                    if self.get_manhattan_distance(star, dancer) <= m:
                        if dancer in graph:
                            graph[dancer].append(star)
                        else:
                            graph[dancer] = []
                            graph[dancer].append(star)
            res = HopcroftKarp(graph).maximum_matching()
            if len(res) == len(dancers) * 2:
                h = m
            else:
                l = m
        return l

    def get_star_score(self, stars):
        score = 0
        for col in range(self.colors):
            score = max(score, self.match(stars, self.dancers[col + 1]))
        return score

    def generate_distribution(self):
        grid = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        total = 0
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.is_occupied((i, j)):
                    continue
                dist = {}
                for color in self.dancers.keys():
                    if color not in dist:
                        dist[color] = 10000000000
                    for pos in self.dancers[color]:
                        dist[color] = min(dist[color],
                                          self.get_manhattan_distance(pos, (i, j)))
                score = 0
                for col in dist:
                    score += 1. / dist[col]
                grid[i][j] = score
                total += score
        points = []
        probs = []
        for i in range(self.board_size):
            print(grid[i])
            for j in range(self.board_size):
                points.append(i * self.board_size + j)
                probs.append(grid[i][j] / total)
        return points, probs

    def put_stars(self):
        points, prob = self.generate_distribution()
        final_stars = set()
        best_score = 10000000000000
        start_time = time.time()
        while time.time() - start_time < 100:
            stars = set()
            while len(stars) < self.dancer_count:
                pt = numpy.random.choice(points, 1, False, prob)
                y = int(pt % self.board_size)
                pt -= y
                x = int(pt / self.board_size)
                if not self.is_occupied((x, y)) and (x, y) not in stars:
                    # check manhattan distance with other stars
                    ok_to_add = True
                    for s in stars:
                        if abs(x - s[0]) + abs(y - s[1]) < self.colors + 1:
                            ok_to_add = False
                            break
                    if ok_to_add:
                        stars.add((x, y))
            temp_score = self.get_star_score(stars)
            print(temp_score)
            if temp_score < best_score:
                best_score = temp_score
                final_stars = stars
        stars = set()
        counter = -1
        srtd = [x for _, x in sorted(zip(prob, points))]
        srtd = srtd[::-1]
        while len(stars) < self.dancer_count:
            counter += 1
            x = srtd[counter]
            y = x % self.board_size
            x -= y
            x = int(x / self.board_size)
            if not self.is_occupied((x, y)) and (x, y) not in stars:
                ok_to_add = True
                for s in stars:
                    if abs(x - s[0]) + abs(y - s[1]) < self.colors + 1:
                        ok_to_add = False
                        break
                if ok_to_add:
                    stars.add((x, y))
        if self.get_star_score(stars) < best_score:
            final_stars = stars
        self.stars = list(final_stars)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1', type=str)
    parser.add_argument('--port', default=9000, type=int)
    parser.add_argument('--name', default='CO', type=str)
    parser.add_argument('--spoiler', default=False, action='store_true')

    args = parser.parse_args()

    random.seed(42)

    if args.spoiler:
        bot = SamplingBot(args.host, args.port, args.name, 'spoiler')
    else:
        bot = SamplingBot(args.host, args.port, args.name)
    bot.run()
