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
        lower = 0
        higher = 1000000
        res = {}
        for i in range(30):
            m = (lower + higher) / 2
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
                higher = m
            else:
                lower = m
        graph = {}
        for dancer in dancers:
            for star in stars:
                if self.get_manhattan_distance(star, dancer) <= lower+1:
                    if dancer in graph:
                        graph[dancer].append(star)
                    else:
                        graph[dancer] = []
                        graph[dancer].append(star)
        res = HopcroftKarp(graph).maximum_matching()
        return lower, res

    def get_star_score(self, stars):
        max_score = 0
        all_matching = {}
        for col in range(self.colors):
            score, matching = self.match(stars, self.dancers[col + 1])
            all_matching[col+1] = matching
            if score > max_score:
                max_score = score
        return max_score, all_matching

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
            # print(grid[i])
            for j in range(self.board_size):
                points.append(i * self.board_size + j)
                probs.append(grid[i][j] / total)
        return points, probs

    def get_probable_centers(self, time_to_take=100):
        points, prob = self.generate_distribution()
        final_stars = set()
        best_matchings = None
        best_score = 10000000000000
        start_time = time.time()
        while time.time() - start_time < time_to_take:
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
            temp_score, matching = self.get_star_score(stars)
            print(temp_score)
            if temp_score < best_score:
                best_score = temp_score
                final_stars = stars
                best_matchings = matching
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
        score, matching = self.get_star_score(stars)
        if score < best_score:
            final_stars = stars
            best_matchings = matching
        return list(final_stars), best_matchings

    def put_stars(self):
        self.stars, _ = self.get_probable_centers(10)

    def get_positions(self, centers, matchings):
        points_available = {}
        all_points = []
        for center in centers:
            found = False
            new_center = center
            radius = 1
            while not found:
                x, y = new_center
                empty_cells = 1
                start = x
                end = x
                while empty_cells < self.colors:
                    if start - 1 >= 0:
                        start -= 1
                        if (start, y) not in self.stars:
                            empty_cells += 1
                    if empty_cells < self.colors:
                        if end + 1 < self.board_size:
                            end += 1
                            if (end, y) not in self.stars:
                                empty_cells += 1
                    if (start, y) in self.stars and (end, y) in self.stars:
                        break
                if empty_cells == self.colors:
                    points_to_add = [(i, y) for i in range(start, end)]
                    point_already_present = False
                    for point, _ in points_to_add:
                        if point in all_points:
                            point_already_present = True
                            break
                    if not point_already_present:
                        points_available[center] = points_to_add
                        found = True
                        all_points.extend(points_to_add)
                        continue

                empty_cells = 1
                start = y
                end = y
                while empty_cells < self.colors:
                    start -= 1
                    if (x, start) not in self.stars:
                        empty_cells += 1
                    if empty_cells < self.colors:
                        end += 1
                        if (x, end) not in self.stars:
                            empty_cells += 1
                    if (x, start) in self.stars and (x, end) in self.stars:
                        break
                if empty_cells == self.colors:
                    points_to_add = [(y, i) for i in range(start, end)]
                    point_already_present = False
                    for point, _ in points_to_add:
                        if point in all_points:
                            point_already_present = True
                            break
                    if not point_already_present:
                        points_available[center] = points_to_add
                        found = True
                        all_points.extend(points_to_add)
                        continue
                    # This is not a feasible center
                    x1, y1 = random.randint(-radius, radius), random.randint(-radius, radius)
                    new_center = max(0, min(self.board_size-1,
                                            new_center[0] + x1)), \
                                 max(0, min(self.board_size-1,
                                            new_center[1] + y1))
        # print(points_available)
        count = 0
        for x in points_available.keys():
            count += len(points_available[x])
        print(count)
        return points_available

    def get_parallel_moves(self):
        centers, matchings = self.get_probable_centers(-1)
        points_available = self.get_positions(centers, matchings)
        position_mapping = []
        availability = {}
        for color in matchings.keys():
            for dancer in self.dancers[color]:
                center = matchings[color][dancer]
                best_point = None
                for i, point in enumerate(points_available[center]):
                    if point not in availability:
                        best_point = point
                        availability[point] = False
                        break
                if best_point is None:
                    print("FUCK!!!")
                    continue
                position_mapping.append((dancer, best_point))
        print(position_mapping)


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
