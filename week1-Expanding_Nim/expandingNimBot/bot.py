import pickle
import os
from moves_table_creation import main as table_creator

class Bot(object):

    def __init__(self):
        if not os.path.isfile("moves_table.pkl"):
            table_creator()

        self.table = pickle.load(open("moves_table.pkl", "rb"))
        self.self_resets = 0
        self.other_resets = 0

        print("Bot Loaded!")

    def set_resets(self, init_resets):
        self.self_resets = init_resets
        self.other_resets = init_resets

    def get_move(self, stones_left, current_max, is_reset):
        move = self.table[stones_left][current_max][self.self_resets][self.other_resets][1 if is_reset else 0]

        if is_reset:
            self.other_resets -= 1
        if move[2]:
            self.self_resets -= 1

        return move[1], move[2]