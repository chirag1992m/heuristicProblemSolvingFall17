from __future__ import print_function

from enum import Enum
import six
import socket

from .game_info import GameInfo


class BaseBot(object):

    class Type(Enum):
        EMPTY = -1
        DONE = 0
        HUNTER = 1
        PREY = 2

        @classmethod
        def tostring(cls, val):
            for k, v in six.iteritems(vars(cls)):
                if v == val:
                    return k

    def __init__(self, host, port, name, visualize=False):
        self.name = name
        self.host = host
        self.port = int(port)

        self.socket = self.make_connection()
        self.buffer = ""
        self.game = GameInfo(visualize=visualize)
        self.mode = self.Type.EMPTY

    def recv_current(self):
        while True:
            self.buffer += str(self.socket.recv(1024), 'utf-8')
            lines = self.buffer.split('\n')
            if len(lines) > 1:
                current_info = lines[0]
                self.buffer = '\n'.join(lines[1:])
                break
        return current_info

    def make_connection(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        return sock

    def make_hunter(self):
        self.mode = self.Type.HUNTER

    def make_prey(self):
        self.mode = self.Type.PREY

    def send_to_game(self, data):
        self.socket.sendall((str(data) + '\n').encode('utf-8'))

    def send_name(self):
        self.send_to_game(self.name)

    def update_game(self, game_update):
        self.game.update_game(game_update)

    def move_hunter(self):
        return -1, []

    def move_prey(self):
        return 0, 0

    def make_move(self):
        if self.mode == self.Type.HUNTER:
            wall_to_add, walls_to_delete = self.move_hunter()
            move_array = [self.game.game_number, self.game.tick, wall_to_add]
            move_array.extend(walls_to_delete)
            move = ' '.join([str(x) for x in move_array])
            self.send_to_game(move)
        elif self.mode == self.Type.PREY:
            x, y = self.move_prey()
            move_array = [self.game.game_number, self.game.tick, x, y]
            move = ' '.join([str(x) for x in move_array])
            self.send_to_game(move)

    def process_info(self, game_stat):
        # print(game_stat)
        if game_stat == "done":
            self.mode = self.Type.DONE
        elif game_stat == "hunter":
            self.make_hunter()
        elif game_stat == "prey":
            self.make_prey()
        elif game_stat == "sendname":
            self.send_name()
        else:
            self.update_game(game_stat)
            self.make_move()

    def start(self):
        while True:
            info = self.recv_current()
            self.process_info(info)
            if self.mode == self.Type.DONE:
                print("Game done!")
                break

    def reset(self):
        self.done()
        self.socket = self.make_connection()
        self.buffer = ""
        self.game = GameInfo()
        self.mode = self.Type.EMPTY

    def done(self):
        self.socket.close()
