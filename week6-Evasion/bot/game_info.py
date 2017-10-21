import numpy as np


class GameInfo:
    def __init__(self):
        self.time_left = None
        self.game_number = None
        self.tick = None
        self.max_walls = None
        self.wall_delay = None
        self.box_size = (300, 300)
        self.wall_time = None
        self.hunter_pos = (0, 0)
        self.hunter_velocity = (0, 0)
        self.prey_pos = (230, 200)
        self.walls = []
        self.box = self.get_game_grid()

    def get_game_grid(self):
        grid = np.zeros(self.box_size, dtype=np.uint8)
        # Put Hunter
        grid[self.hunter_pos] = 2
        # Put Prey
        grid[self.prey_pos] = 3

        # Put Walls
        for wall in self.walls:
            if wall[0] == 0:
                _, y, x1, x2 = wall
                grid[x1:x2+1][y] = 1
            elif wall[0] == 1:
                _, x, y1, y2 = wall
                grid[x][y1:y2+1] = 1
            elif wall[0] == 2:
                _, x1, x2, y1, y2, direction = wall
                # Build the Diagonal Wall
            else:
                _, x1, x2, y1, y2, direction = wall
                # Build the Counter-Diagonal Wall
        return grid

    @staticmethod
    def get_walls(num, wall_info):
        walls = []
        current = 0
        while current < len(wall_info):
            if wall_info[current] == 0:     # Horizontal Wall
                walls.append((wall_info[current], wall_info[current+1],
                              wall_info[current+2], wall_info[current+3]))
                current += 4
            elif wall_info[current] == 1:   # Vertical Wall
                walls.append((wall_info[current], wall_info[current+1],
                              wall_info[current+2], wall_info[current+3]))
                current += 4
            elif wall_info[current] == 2:
                walls.append((wall_info[current],
                              wall_info[current+1], wall_info[current+2],
                              wall_info[current+3], wall_info[current+4],
                              wall_info[current+5]))
                current += 6
            elif wall_info[current] == 3:
                walls.append((wall_info[current],
                              wall_info[current + 1], wall_info[current + 2],
                              wall_info[current + 3], wall_info[current + 4],
                              wall_info[current + 5]))
                current += 6
            else:
                raise ValueError("Wall info incorrect: {}, {}".format(num, ' '.join(wall_info)))
        if len(walls) > num:
            raise ValueError("Wall info incorrect: {}, {}".format(num, ' '.join(wall_info)))
        return walls

    def update_game(self, update):
        all_info = [int(x) for x in update.split(' ')]
        self.time_left = all_info[0]
        self.game_number = all_info[1]
        self.tick = all_info[2]
        self.max_walls = all_info[3]
        self.wall_delay = all_info[4]
        # Fixed for the game, so ignoring
        # self.box_size = (all_info[5], all_info[6])
        self.wall_time = all_info[7]
        self.hunter_pos = all_info[8], all_info[9]
        self.hunter_velocity = all_info[10], all_info[11]
        self.prey_pos = all_info[12], all_info[13]
        num_walls = all_info[14]
        wall_info = all_info[15:]
        self.walls = self.get_walls(num_walls, wall_info)
