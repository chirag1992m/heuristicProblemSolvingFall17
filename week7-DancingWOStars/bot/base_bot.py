import argparse
import random

from .client import Client


class BaseBot(object):
    def __init__(self, host, port, name, role='choreographer'):
        self.client = Client(host=host, port=port)
        self.client.send(name)
        self.role = role

        self.board_size, self.colors, self.dancer_count = self.get_parameters()
        self.dancers = self.process(self.client.receive())
        self.stars = []
        self.lines_info = []

    def get_parameters(self):
        parameters = self.client.receive()
        return map(int, parameters.split())

    def get_parallel_moves(self):
        # pick 5 random dancers from dancers
        for i in range(5):
            moves, moved_dancer = [], []
            while len(moves) < 5:
                # pick random dancer
                picked_color = random.sample(self.dancers.keys(), 1)[0]
                picked_dancer = random.sample(self.dancers[picked_color], 1)[0]
                x, y = picked_dancer
                while (x, y) in moved_dancer:
                    continue
                c = random.sample([(1, 0), (-1, 0), (0, 1), (0, -1)], 1)[0]
                x2 = x + c[0]
                y2 = y + c[1]
                if (x2, y2) in self.stars:
                    continue
                if x2 not in range(self.board_size) or y2 not in range(self.board_size):
                    continue
                moves.append(((x, y), (x2, y2)))
                moved_dancer.append((x, y))
                self.dancers[picked_color].remove((x, y))
                self.dancers[picked_color].append((x2, y2))
            yield moves

    def is_occupied(self, point):
        for color in self.dancers.keys():
            if point in self.dancers[color]:
                return True
        if point in self.stars:
            return True
        return False

    def put_stars(self):
        self.stars = []
        while len(self.stars) < self.dancer_count:
            x = random.randint(0, self.board_size - 1)
            y = random.randint(0, self.board_size - 1)
            if not self.is_occupied((x, y)):
                # check manhattan distance with other stars
                ok_to_add = True
                for s in self.stars:
                    if abs(x - s[0]) + abs(y - s[1]) < self.colors + 1:
                        ok_to_add = False
                        break
                if ok_to_add:
                    self.stars.append((x, y))

    def send_parallel_moves(self, all_moves):
        # count = 0
        for parallel_move in all_moves:
            if len(parallel_move) == 0:
                break
            string_builder = [str(len(parallel_move))]
            for start, end in parallel_move:
                x_1, y_1 = tuple(map(str, start))
                x_2, y_2 = tuple(map(str, end))
                string_builder.extend([x_1, y_1, x_2, y_2])
            to_send = ' '.join(string_builder)
            print("Sending move: " + to_send)
            self.client.send(to_send)
            # count += 1
            # if count > 1000:
            #     break
        self.client.send("DONE")

    def send_stars(self):
        string_builder = []
        for position in self.stars:
            x, y = tuple(map(str, position))
            string_builder.extend([x, y])
        to_send = ' '.join(string_builder)
        print("Putting stars at: " + to_send)
        self.client.send(to_send)

    def get_stars_from_server(self):
        positions = self.client.receive().split()
        assert len(positions) % 2 == 0, "Star positions not even"

        stars = []
        for i in range(0, len(positions), 2):
            stars.append((int(positions[i]), int(positions[i + 1])))
        return stars

    def run(self):
        if self.role == 'choreographer':
            self.stars = self.get_stars_from_server()
            self.send_parallel_moves(self.get_parallel_moves())
            self.client.send(' '.join(self.lines_info))
        else:
            self.put_stars()
            self.send_stars()

    def process(self, game_file):
        dancers = dict()
        color = 0
        for line in game_file.splitlines():
            if line.startswith('Dancer'):
                color += 1
                dancers[color] = []
                continue
            dancers[color].append(tuple(map(int, line.split())))
        for c in dancers.keys():
            assert len(dancers[c]) == self.dancer_count, "Something wrong with " \
                                                         "received dancers: {}".format(dancers)
        return dancers

    def get_manhattan_distance(self, point1, point2):
        return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1', type=str)
    parser.add_argument('--port', default=9000, type=int)
    parser.add_argument('--name', default='CO', type=str)
    parser.add_argument('--spoiler', default=False, action='store_true')

    args = parser.parse_args()

    random.seed(42)

    if args.spoiler:
        bot = BaseBot(args.host, args.port, args.name, 'spoiler')
    else:
        bot = BaseBot(args.host, args.port, args.name)
    bot.run()
