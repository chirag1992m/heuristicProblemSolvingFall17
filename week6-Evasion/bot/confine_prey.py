import argparse
from base_bot import BaseBot
import random
import math

class ConfineBot(BaseBot):

    def __init__(self, host, port, name, visualize=False, seed=42):
        super().__init__(host=host, port=port, name=name, visualize=visualize)
        random.seed(seed)
        self.wall_separated = 0
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
        if((pos[0] < 0 ) or ( pos[0] >= 300 ) or ( pos[1] < 0 ) or ( pos[1] >= 300)):
            return True
        if(self.game.grid[pos[0]][pos[1]] == 1):
            return True
        return False

    def get_next_hunter_pos(self):
        temp_pos = (self.game.hunter_pos[0] + self.game.hunter_velocity[0], self.game.hunter_pos[1] + self.game.hunter_velocity[1])
        if(not self.isOccupied(temp_pos)):
            return temp_pos
        else:
            oneRight = (self.game.hunter_pos[0]+self.game.hunter_velocity[0], self.game.hunter_pos[1])
            oneUp = (self.game.hunter_pos[0], self.game.hunter_pos[1] + self.game.hunter_velocity[1])

            if (self.isOccupied(oneRight) and self.isOccupied(oneUp)):
                return self.game.hunter_pos
            elif (self.isOccupied(oneRight)):
                return (self.game.hunter_pos[0], self.game.hunter_pos[1] + self.game.hunter_velocity[1])
            elif (self.isOccupied(oneUp)):
                return (self.game.hunter_pos[0] + self.game.hunter_velocity[0], self.game.hunter_pos[1])
            else:
                twoUpOneRight = (self.game.hunter_pos[0] + self.game.hunter_velocity[0], self.game.hunter_pos[1] + self.game.hunter_velocity[1]*2)
                oneUpTwoRight = (self.game.hunter_pos[0] + self.game.hunter_velocity[0]*2, self.game.hunter_pos[1] + self.game.hunter_velocity[1])
                tuor = 0
                outr = 0
                if(self.isOccupied(twoUpOneRight)):
                    tuor = 1
                if(self.isOccupied(oneUpTwoRight)):
                    outr = 1

                if((tuor==1 and outr==1) or (tuor==0 and outr==0)):
                    return self.game.hunter_pos
                elif (tuor==1):
                    return twoUpOneRight
                else:
                    return oneUpTwoRight
        return temp_pos


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
        hunter_next_pos = self.get_next_hunter_pos()
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
            hunter_next_pos = self.get_next_hunter_pos()
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

    '''
    def move_hunter(self):
        normal_vel = self.game.hunter_velocity[0] + self.game.hunter_velocity[1]
        normal_vel /= math.sqrt(2)
        temp_h = self.game.hunter_pos + self.game.hunter_vel
        temp_p = self.game.prey_pos - self.game.hunter_vel
        options = []
        if(self.sign(temp_h[0] - temp_p[0]) != self.sign(self.game.hunter_pos[0] - self.game.prey_pos[0])):
            options.append(0)
        if(self.sign(temp_h[1] - temp_p[1]) != self.sign(self.game.hunter_pos[1] - self.game.prey_pos[1])):
            options.append(1)
        if(self.sign(temp_h[0] + temp_h[1] - temp_p[0] - temp_p[1]) != self.sign(self.game.hunter_pos[1] + self.game.hunter_pos[0] - self.game.prey_pos[1] - self.game.prey_pos[0])):
            options.append(2)
        if(self.sign(temp_h[0] - temp_h[1] - temp_p[0] + temp_p[1]) != self.sign(self.game.hunter_pos[0] - self.game.hunter_pos[1] + self.game.prey_pos[1] - self.game.prey_pos[0])):
            options.append(3)

        wall = random.randint(0, 4)
        to_delete = []
        for wall_idx in range(len(self.game.walls)):
            if random.random() < .1:
                to_delete.append(wall_idx)
        return wall, to_delete
    '''

    def move_prey(self):
        y = self.yy
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
            return x,y


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
