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
        self.stars, _ = self.get_probable_centers(100)

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
                    points_to_add = [(i, y) for i in range(start, end+1)]
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
                    points_to_add = [(y, i) for i in range(start, end+1)]
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
        print(len(centers))
        print(len(points_available.keys()))
        print(self.colors)
        print(len(self.dancers.keys()))
        count = 0
        for x in points_available.keys():
            while len(points_available[x]) > self.colors:
                print("wtf!")
                points_available[x].pop()
            count += len(points_available[x])
        count2 = 0
        for x in self.dancers.keys():
            count2 += len(self.dancers[x])
        print("Count: {}, dancers: {}".format(count, count2))
        # exit()
        return points_available

    def get_parallel_moves(self):
        centers, matchings = self.get_probable_centers(50)
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
        for center in points_available.keys():
            self.lines_info.append(str(points_available[center][0][0]))
            self.lines_info.append(str(points_available[center][0][1]))
            self.lines_info.append(str(points_available[center][self.colors-1][0]))
            self.lines_info.append(str(points_available[center][self.colors-1][1]))
        init_pos = []
        final_pos = []
        for (pos1, pos2) in position_mapping:
            init_pos.append(pos1)
            final_pos.append(pos2)
        cur_pos = init_pos
        dir = [random.randint(0, 1) for _ in range(len(cur_pos))]
        while (cur_pos != final_pos):
            returnThis, next_pos, dd = self.get_next_moves(cur_pos, final_pos, dir)
            cur_pos = next_pos
            dir = dd
            yield returnThis

    def get_next_moves(self, init_pos, final_pos, dir):
        new_grid = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        for star in self.stars:
            new_grid[star[0]][star[1]] = 1
        for pos in init_pos:
            new_grid[pos[0]][pos[1]] = 1
        result = [] #omitting dancers which don't move. Return this to server
        result2 = [] #without omission. This will be used as the next positions of the dancers
        for i in range(len(init_pos)):
            cur = init_pos[i]
            fin = final_pos[i]
            dd = dir[i]
            if(cur == fin):
                new_grid[cur[0]][cur[1]] = 1
                continue
            print(cur, fin, dd)
            deltaX = -1
            deltaY = -1
            # print(fin, cur)
            if(fin[0] > cur[0]):
                deltaX = 1
            elif(fin[0] == cur[0]):
                deltaX = 0
            if(fin[1] > cur[1]):
                deltaY = 1
            elif(fin[1] == cur[1]):
                deltaY = 0
            new_pos = cur
            if(dd == 0):
                if(deltaY != 0 and cur[1]+deltaY >=0 and cur[1]+deltaY < self.board_size and new_grid[cur[0]][cur[1] + deltaY] == 0):
                    new_pos = (cur[0], cur[1] + deltaY)
                elif(deltaX != 0 and cur[0]+deltaX >=0 and cur[0]+deltaX < self.board_size and new_grid[cur[0] + deltaX][cur[1]] == 0):
                    new_pos = (cur[0] + deltaX, cur[1])
                else:
                    if(deltaX == 0 and cur != fin and cur[1]+deltaY >=0 and cur[1]+deltaY < self.board_size  and (cur[0],cur[1] + deltaY) in self.stars):
                        if(cur[0] + 1 < self.board_size and new_grid[cur[0]+1][cur[1]] == 0):
                            new_pos = (cur[0]+1, cur[1])
                            dir[i] = 0
                        elif(cur[0] - 1 >=0 and new_grid[cur[0]-1][cur[1]] == 0):
                            new_pos = (cur[0] - 1, cur[1])
                            dir[i] = 0
                    elif(deltaY == 0 and cur != fin and cur[0]+deltaX >=0 and cur[0]+deltaX < self.board_size and (cur[0] + deltaX,cur[1]) in self.stars):
                        if(cur[1] + 1 < self.board_size and new_grid[cur[0]][cur[1]+1] == 0):
                            new_pos = (cur[0], cur[1]+1)
                            dir[i] = 1
                        elif(cur[1] - 1>=0 and new_grid[cur[0]][cur[1]-1] == 0):
                            new_pos = (cur[0], cur[1]-1)
                            dir[i] = 1
                new_grid[new_pos[0]][new_pos[1]] = 1
                if(new_pos != cur):
                    result.append((cur, new_pos))
                result2.append(new_pos)
            else:
                if(deltaX != 0 and cur[0]+deltaX >=0 and cur[0]+deltaX < self.board_size and new_grid[cur[0] + deltaX][cur[1]] == 0):
                    new_pos = (cur[0] + deltaX, cur[1])
                elif(deltaY != 0 and new_grid[cur[0]][cur[1] + deltaY] == 0):
                    new_pos = (cur[0], cur[1] + deltaY)
                else:
                    if(deltaY == 0 and cur != fin and cur[0]+deltaX >=0 and cur[0]+deltaX < self.board_size and (cur[0] + deltaX,cur[1]) in self.stars):
                        if(cur[1] + 1 < self.board_size and new_grid[cur[0]][cur[1]+1] == 0):
                            new_pos = (cur[0], cur[1]+1)
                            dir[i] = 1
                        elif(cur[1] - 1 >=0 and new_grid[cur[0]][cur[1]-1] == 0):
                            new_pos = (cur[0], cur[1]-1)
                            dir[i] = 1
                    elif(deltaX == 0 and cur != fin and cur[1]+deltaY >=0 and cur[1]+deltaY < self.board_size  and (cur[0],cur[1] + deltaY) in self.stars):
                        if(cur[0] + 1 < self.board_size and new_grid[cur[0]+1][cur[1]] == 0):
                            new_pos = (cur[0]+1, cur[1])
                            dir[i] = 0
                        elif(cur[0] -1 >= 0 and new_grid[cur[0]-1][cur[1]] == 0):
                            new_pos = (cur[0] - 1, cur[1])
                            dir[i] = 0
                new_grid[new_pos[0]][new_pos[1]] = 1
                if(new_pos != cur):
                    result.append((cur, new_pos))
                result2.append(new_pos)

        return result, result2, dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1', type=str)
    parser.add_argument('--port', default=9000, type=int)
    parser.add_argument('--name', default='CO', type=str)
    parser.add_argument('--spoiler', default=False, action='store_true')

    args = parser.parse_args()

    random.seed(234)

    if args.spoiler:
        bot = SamplingBot(args.host, args.port, args.name, 'spoiler')
    else:
        bot = SamplingBot(args.host, args.port, args.name)
    bot.run()
