import numpy as np
import visdom


class GameInfo:
    def __init__(self, visualize=False):
        self.time_left = None
        self.game_number = None
        self.tick = None
        self.max_walls = None
        self.wall_delay = None
        self.box_size = (300, 300)
        self.wall_time = None
        self.hunter_pos = (0, 0)
        self.hunter_velocity = (1, 1)
        self.prey_pos = (230, 200)
        self.walls = []
        self.figure, self.viz_win = None, None
        if visualize:
            self.figure = visdom.Visdom(env='evasion')
        self.grid = self.get_game_grid()

    def get_game_grid(self):
        grid = np.zeros(self.box_size, dtype=np.float32)
        # Put Hunter
        grid[self.hunter_pos] = 2
        # Put Prey
        grid[self.prey_pos] = 3

        # Put Walls
        for wall in self.walls:
            # print("Adding wall: {}".format(wall))
            if wall[0] == 0:
                _, y, x1, x2 = wall
                grid[x1:min(299, x2+1), y] = 1
            elif wall[0] == 1:
                _, x, y1, y2 = wall
                grid[x, y1:min(299, y2+1)] = 1
            elif wall[0] == 2:
                _, x1, x2, y1, y2, direction = wall
                if direction == 0:
                    y = y1
                    for x in range(x1, x2):
                        grid[x][min(299, y)] = 1
                        if x != x2:
                            grid[x+1][y] = 1
                            y += 1
                else:
                    x = x1
                    for y in range(y1, y2+1):
                        grid[min(299, x)][y] = 1
                        if y != y2:
                            grid[x][y+1] = 1
                            x += 1
            else:
                _, x1, x2, y1, y2, direction = wall
                if direction == 0:
                    y = y1
                    for x in range(x1, x2+1):
                        grid[x][max(0, y)] = 1
                        if x != x2:
                            grid[x+1][y] = 1
                            y -= 1
                else:
                    y = y1
                    for x in range(x1, x2+1):
                        grid[x][max(0, y)] = 1
                        if x != x2:
                            grid[x][y-1] = 1
                            y -= 1
        if self.figure:
            colored_grid = np.ones((3, ) + grid.shape, dtype=np.float32)
            colored_grid[:, grid == 1] = 0.
            colored_grid[:, grid == 2] = 0.
            colored_grid[0, grid == 2] = 1.
            colored_grid[:, grid == 3] = 0.
            colored_grid[2, grid == 3] = 1.
            self.viz_win = self.figure.image(img=colored_grid, win=self.viz_win)
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
        self.grid = self.get_game_grid()

    @staticmethod
    def is_cell_occupied(grid, cell):
        if (cell[0] < 0 or cell[0] >= 300) or (cell[1] < 0 or cell[1] >= 300):
            return True
        if grid[cell] == 1:
            return True
        return False

    @staticmethod
    def move_player(grid, pos, move):
        target_pos = pos[0] + move[0], pos[1] + move[1]
        if not GameInfo.is_cell_occupied(grid, target_pos):
            return target_pos, move
        if move[0] ==  0 or move[1] == 0:
            if move[0]:
                move = (-move[0], move[1])
            else:
                move = (move[0], -move[1])
        else:
            vert = GameInfo.is_cell_occupied(grid, (pos[0], target_pos[1]))
            hort = GameInfo.is_cell_occupied(grid, (target_pos[0], pos[1]))
            if vert and hort:
                move = (-move[0], -move[1])
            elif hort:
                move = (-move[0], move[1])
                pos = (pos[0], target_pos[1])
            elif vert:
                move = (move[0], -move[1])
                pos = (target_pos[0], pos[1])
            else:
                two_vert_one_hort = grid, (target_pos[0], target_pos[1] + move[1])
                one_vert_two_hort = grid, (target_pos[0] + move[0], target_pos[1])
                if ((two_vert_one_hort and one_vert_two_hort)
                    or not (two_vert_one_hort or one_vert_two_hort)):
                    move = (-move[0], -move[1])
                elif two_vert_one_hort:
                    move = (-move[0], move[1])
                    pos = (pos[0], target_pos[1])
                else:
                    move = (move[0], -move[1])
                    pos = (target_pos[0], pos[1])
        return pos, move

    @staticmethod
    def simulate_move(game_state, hunter_move, prey_move):
        grid = np.copy(game_state['grid'])
        hunter_velocity = game_state['hunter_velocity']
        hunter_pos = np.where(grid == 2)
        prey_pos = np.where(grid == 3)

        hunter_pos_x, hunter_pos_y = hunter_pos[0][0], hunter_pos[1][0]
        prey_pos_x, prey_pos_y = prey_pos[0][0], prey_pos[1][0]

        # Move the hunter
        hunter_pos, hunter_velocity = GameInfo.move_player(grid,
                                                           (hunter_pos_x, hunter_pos_y),
                                                           hunter_velocity)
        grid[hunter_pos_x, hunter_pos_y] = 0
        grid[hunter_pos] = 2

        if hunter_move == 1:
            # Make the horizontal wall
            pass
        elif hunter_move == 2:
            # Make the vertical wall
            pass
        elif hunter_move == 3:
            # Make diagonal wall
            pass
        elif hunter_move == 4:
            # Make the counter-diagonal wall
            pass

        # move the prey
        prey_pos, _ = GameInfo.move_player(grid, (prey_pos_x, prey_pos_y), prey_move)
        grid[prey_pos_x, prey_pos_y] = 0
        grid[prey_pos] = 3

        return {
            'grid': grid,
            'hunter_velocity': hunter_velocity
        }
