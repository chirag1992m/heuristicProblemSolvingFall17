import argparse
from base_bot import BaseBot
import random
import math
from math import fabs

class ConfineBot(BaseBot):

    def __init__(self, host, port, name, visualize=False, seed=42):
        super().__init__(host=host, port=port, name=name, visualize=visualize)
        random.seed(seed)
        self.wall_separated = 0
        self.last_walls = []
        self.center = (150,150)
        self.delay = 0
        self.flag = 0
        self.tick = 0
        self.xx = 1
        self.yy = 1

    def sign_val(self, a):
        if(a == 0):
            return 0
        elif(a < 0):
            return -1
        else:
            return 1

    def sign(self, wall, pos):
        if(wall[0] == 0):
            return self.sign_val(wall[1] - pos[1])
        elif (wall[0] == 1):
            return self.sign_val(wall[1] - pos[0])
        else:
            _, x1, x2, y1, y2 = wall
            slope = (y2 - y1)/(x2 - x1)
            c = y1 - slope*x1
            return sign_val(pos[1] - slope*pos[0] - c)


    def dist_to_wall(self, wall, pos):
        if(wall[0] == 0):
            return abs(wall[1] - pos[1])
        elif(wall[0] == 1):
            return abs(wall[1] - pos[0])
        else:
            _,x1,x2,y1,y2 = wall
            dist = (y2 - y1)*pos[0] + (x1 - x2)*pos[1] + x2*y1 - y2*x1
            dist /= sqrt((y2 - y1)*(y2-y1) + (x2-x1)*(x2-x1))
            return abs(dist)

    def isOccupied(self, pos):
        self.game.grid = self.game.get_game_grid()
        if((pos[0] < 0 ) or ( pos[0] >= 300 ) or ( pos[1] < 0 ) or ( pos[1] >= 300)):
            return True
        if fabs(self.game.grid[pos[0]][pos[1]]-1) < 0.001:
            return True
        return False

    def get_next_hunter_pos(self, pos, vel):
        temp_pos = (pos[0] + vel[0], pos[1] + vel[1])
        temp_vel = vel
        if(not self.isOccupied(temp_pos)):
            return temp_pos, vel
        else:
            if vel[0] == 0:
                return pos, (vel[0], -vel[1])
            if vel[1] == 0:
                return pos, (-vel[0], vel[1])
            oneRight = (pos[0]+vel[0], pos[1])
            oneUp = (pos[0], pos[1] + vel[1])

            if (self.isOccupied(oneRight) and self.isOccupied(oneUp)):
                return pos, (-vel[0], -vel[1])
            elif (self.isOccupied(oneRight)):
                return (pos[0], pos[1] + vel[1]), (-vel[0], vel[1])
            elif (self.isOccupied(oneUp)):
                return (pos[0] + vel[0], pos[1]), (vel[0], -vel[1])
            else:
                twoUpOneRight = (pos[0] + vel[0], pos[1] + vel[1]*2)
                oneUpTwoRight = (pos[0] + vel[0]*2, pos[1] + vel[1])
                tuor = 0
                outr = 0
                if(self.isOccupied(twoUpOneRight)):
                    tuor = 1
                if(self.isOccupied(oneUpTwoRight)):
                    outr = 1

                if((tuor==1 and outr==1) or (tuor==0 and outr==0)):
                    return pos, (-vel[0], -vel[1])
                elif (tuor==1):
                    return twoUpOneRight, (-vel[0], vel[1])
                else:
                    return oneUpTwoRight, (vel[0], -vel[1])
        return temp_pos, temp_vel


    def move_hunter(self):
        if(self.tick >= 100 and self.flag == 0):
            self.flag = 1
            return 2, []
        self.tick += 1
        to_delete = []
        if(self.delay != 0):
            self.delay -= 1
        if(self.delay != 0):
            return 0, []
        hunter_next_pos, hunter_next_vel = self.get_next_hunter_pos(self.game.hunter_pos, self.game.hunter_velocity)
        self.wall_separated = 0
        for wall_idx in range(len(self.game.walls)):
            wall = self.game.walls[wall_idx]
            if(self.sign(wall, self.game.hunter_pos) != self.sign(wall, self.game.prey_pos)):
                self.wall_separated = 1
        options = []
        if(self.wall_separated == 1):
            # print("Wall separated")
            for wall_idx in range(len(self.game.walls)):
                wall = self.game.walls[wall_idx]
                if(self.sign(wall, self.game.hunter_pos) == -self.sign(wall, self.game.prey_pos)):
                    if(self.dist_to_wall(wall, self.game.hunter_pos) <= 2 and self.dist_to_wall(wall, self.game.hunter_pos) >= self.dist_to_wall(wall, hunter_next_pos)): #and not if this wall was recently added
                        to_delete.append(wall_idx)
                        if(wall[0] == 0):
                            options.append(1)
                        elif(wall[0] == 1):
                            options.append(2)
            self.wall_separated = 0
            for wall_idx in range(len(self.game.walls)):
                wall = self.game.walls[wall_idx]
                if(self.sign(wall, self.game.hunter_pos) != self.sign(wall, self.game.prey_pos)):
                    self.wall_separated = 1
        wmax = 0
        wmin = 300
        hmax = 0
        hmin = 300

        for wall in self.game.walls:
            if(wall[0] == 0 and wall[1] >= self.game.hunter_pos[1]):
                hmin = min(hmin, wall[1])
            if(wall[0] == 0 and wall[1] <= self.game.hunter_pos[1]):
                hmax = max(hmax, wall[1])
            if(wall[0] == 1 and wall[1] >= self.game.hunter_pos[0]):
                wmin = min(wmin, wall[1])
            if(wall[0] == 1 and wall[1] <= self.game.hunter_pos[0]):
                wmax = max(wmax, wall[1])
        if(len(options) != 0):
            wall = options[random.randint(0, len(options)-1)]
            print("")
            print(self.game.walls)
            print("deleting here", wall, to_delete)
            self.delay = self.game.wall_delay + 1
            return wall, to_delete
        options = []
        if(self.wall_separated == 0):
            hunter_next_pos, hunter_next_vel = self.get_next_hunter_pos(self.game.hunter_pos, self.game.hunter_velocity)
            if(abs(self.game.hunter_pos[1] - self.game.prey_pos[1]) < 2):
                options.append(1)
            if(abs(self.game.hunter_pos[0] - self.game.prey_pos[0]) < 2):
                options.append(2)
            # horizontal wall:
            if(abs(self.game.hunter_pos[1] - self.game.prey_pos[1]) < abs(self.game.prey_pos[1] - hunter_next_pos[1])):
                # print(self.game.hunter_pos)
                # print(self.game.prey_pos)
                # print(hunter_next_pos)
                if (1 not in options):
                    options.append(1)
            if(abs(self.game.hunter_pos[0] - self.game.prey_pos[0]) < abs(self.game.prey_pos[0] - hunter_next_pos[0])):
                if(2 not in options):
                    options.append(2)
            if(hmin - hmax < 12):
                try:
                    options.remove(1)
                except ValueError:
                    pass
            if(wmin - wmax < 12):
                try:
                    options.remove(2)
                except ValueError:
                    pass
        if(len(options) == 0):
            if(len(to_delete)!=0):
                print("Just deleting", to_delete)
            return 0, to_delete
        self.delay = self.game.wall_delay + 1
        wall = options[random.randint(0, len(options)-1)]
        temp_wall = 0, self.game.hunter_pos[1], 0, 0
        if(wall == 2):
            temp_wall = 1, self.game.hunter_pos[0], 0, 0
        print("")
        print(to_delete)
        print(self.game.walls)
        print("wall delay: ", self.delay)
        print("hunter_pos", self.game.hunter_pos)
        print("hunter_next_pos", hunter_next_pos)
        print("prey_pos", self.game.prey_pos)
        print("wall_separated: ", self.wall_separated)
        print("options", options)
        print("removing: ", to_delete)
        for wall_idx in range(len(self.game.walls)):
            curr_wall = self.game.walls[wall_idx]
            if(curr_wall[0] == wall-1):
                print("wall ", curr_wall)
                print("temp wall: ", temp_wall)
                print(self.sign(curr_wall, hunter_next_pos))
                print(self.sign(temp_wall, hunter_next_pos))
                print(self.sign(curr_wall, self.game.prey_pos))
                print(self.sign(temp_wall, self.game.prey_pos))
                if(self.sign(curr_wall, hunter_next_pos) == self.sign(temp_wall, hunter_next_pos)):
                    if(self.sign(curr_wall, self.game.prey_pos) == self.sign(temp_wall, self.game.prey_pos)):
                        print(curr_wall)
                        if(self.dist_to_wall(curr_wall, self.game.prey_pos) > self.dist_to_wall(temp_wall, self.game.prey_pos)):
                            if(wall_idx not  in to_delete):
                                print("deleting this wall here ................... ", self.game.walls[wall_idx])
                                pass
                                to_delete.append(wall_idx)

        print("Finally deleting and adding", to_delete, wall)
        return wall, to_delete

    def get_dist(self, pos):
        walls = self.game.walls
        min_dist = min(pos[0], pos[1])
        min_dist = min(min_dist, 300 - pos[0])
        min_dist = min(min_dist, 300 - pos[1])
        for wall in self.game.walls:
            temp_dist = self.dist_to_wall(wall, pos)
            if temp_dist < min_dist:
                min_dist = temp_dist
        return min_dist

    def find_center(self):
        if self.last_walls == self.game.walls:
            return self.center
        bfs_queue = []
        cur_pos = self.game.prey_pos
        bfs_queue.append(cur_pos)
        vis = [[0 for _ in range(300)] for _ in range(300)]
        vis[cur_pos[0]][cur_pos[1]] = 1
        cur_center = cur_pos
        cur_dist = self.get_dist(cur_pos)
        num_visited = 1
        sum_x = cur_pos[0]
        sum_y = cur_pos[1]
        while len(bfs_queue) > 0:
            front = bfs_queue.pop(0)
            for i in range(-1, 2):
                for j in range(-1, 2):
                    xx = front[0] + i
                    yy = front[1] + j
                    if self.isOccupied((xx,yy)):
                        continue
                    if (vis[xx][yy] == 0):
                        vis[xx][yy] = 1
                        num_visited += 1
                        sum_x += xx
                        sum_y += yy
                        temp_dist = self.get_dist((xx, yy))
                        if temp_dist > cur_dist:
                            cur_dist = temp_dist
                            cur_center = (xx,yy)
                        bfs_queue.append((xx, yy))
        self.last_walls = self.game.walls
        self.center =  (sum_x//num_visited, sum_y//num_visited)
        return cur_center

    def move_prey(self):
        hunter_pos_set = []
        next_hunter_pos = self.game.hunter_pos
        next_hunter_vel = self.game.hunter_velocity
        self.game.grid = self.game.get_game_grid()
        for _ in range(9):
            next_hunter_pos, next_hunter_vel = self.get_next_hunter_pos(next_hunter_pos, next_hunter_vel)
            for i in range(-4, 5):
                for j in range(-4, 5):
                    if(abs(i) + abs(j) < 5):
                        temp_pos = (next_hunter_pos[0] + i, next_hunter_pos[1] + j)
                        if temp_pos not in hunter_pos_set:
                            hunter_pos_set.append(temp_pos)
        center = self.find_center()
        cur_pos = self.game.prey_pos
        print(cur_pos, center)
        best_dist = 1000
        ii = 0
        jj = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                xx = cur_pos[0] + i
                yy = cur_pos[1] + j
                if self.isOccupied((xx,yy)):
                    continue
                if (xx,yy) not in hunter_pos_set and abs(xx - center[0]) + abs(yy - center[1]) < best_dist:
                    best_dist = abs(xx - center[0]) + abs(yy - center[1])
                    ii = i
                    jj = j
        print("sending movement")
        print(ii, jj)
        print(self.game.grid[238][180])
        print(self.game.walls)
        print(self.isOccupied((238, 180)))
        return (ii, jj)
        '''y = self.yy
        x = self.xx
        if(self.isOccupied((self.game.prey_pos[0]+x,self.game.prey_pos[1] + y))):
            self.yy = -self.yy
            y = self.yy
        else:
            return x,y
        if(self.isOccupied((self.game.prey_pos[0]+x,self.game.prey_pos[1] + y))):
            for i in range(0,2):
                for j in range(-1, 2):
                    if(not self.isOccupied((self.game.prey_pos[0]+i, self.game.prey_pos[1] + j))):
                        self.xx = i
                        self.yy = j
                        return i,j
        else:
            return x,y'''


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', default='127.0.0.1', type=str)
    parser.add_argument('--port', default=9001, type=int)
    parser.add_argument('--name', default='chirag-ojas', type=str)
    parser.add_argument('--viz', default=False, action='store_true')
    args = parser.parse_args()

    client = ConfineBot(args.ip, args.port, args.name, visualize=args.viz)
    client.start()
    client.done()
