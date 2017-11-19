import socket, time, random, math
import argparse


# implements a random bot
class Client:
    def __init__(self, host, port, name):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = name

        # hard-coded game info
        self.grid_size = 1000
        self.min_dist = 66

        # connect to server and get game info
        self.sock.connect((host, port))
        self.num_players, self.num_stone, self.player_number = map(int, self.__receive_move())
        self.grid = [[0] * self.grid_size for _ in range(self.grid_size)]
        self.moves = []     # store history of moves

        # send name to serer
        self.__send(self.name)
        self.winner = -1
        print("Client initialized")

    def __receive(self):
        return self.sock.recv(2048).decode('utf-8')

    def __send(self, string):
        self.sock.sendall(string.encode('utf-8'))

    def __receive_move(self):
        return [int(i) for i in self.__receive().split()]

    def __send_move(self, move_row, move_col):
        self.__send("{} {}".format(move_row, move_col))

    def set_winner(self, last_move_data):
        winner_score = -1
        for i in range(self.num_players):
            if winner_score < last_move_data[i + 1]:
                self.winner = i+1
                winner_score = last_move_data[i + 1]

    @staticmethod
    def __compute_distance(row1, col1, row2, col2):
        return math.sqrt((row2 - row1)**2 + (col2 - col1)**2)

    def __is_valid_move(self, move_row, move_col):
        for move in self.moves:
            if self.__compute_distance(move_row, move_col, move[0], move[1]) < self.min_dist:
                return False
        return True

    # your algorithm goes here
    # a naive random algorithm is provided as a placeholder
    def get_move(self):
        while True:
            move_row = random.randint(0, 999)
            move_col = random.randint(0, 999)
            if self.__is_valid_move(move_row, move_col):
                break
        return move_row, move_col

    def start(self):
        for p in range(self.num_players):
            while True:
                move_data = self.__receive_move()
                print("Got move {}".format(move_data))
                # check if game is over
                if int(move_data[0]) == 1:
                    self.set_winner(move_data)
                    break

                # scores
                scores = []
                for i in range(self.num_players):
                    scores.append(move_data[i + 1])
                # new moves
                new_moves = move_data[self.num_players + 1:]
                num_new_moves = int(len(new_moves) / 3)
                # sanity check
                if num_new_moves * 3 != len(new_moves):
                    print("Error: error parsing list of new moves")

                # insert new moves into the grid
                for i in range(num_new_moves):
                    move_row = int(new_moves[3 * i])
                    move_col = int(new_moves[3 * i + 1])
                    player = int(new_moves[3 * i + 2])
                    # sanity check, this should always be true
                    if player > 0:
                        self.grid[move_row][move_col] = player
                        self.moves.append((move_row, move_col, player))
                    else:
                        print("Error: player info incorrect")

                # make move
                my_move_row, my_move_col = self.get_move()
                self.moves.append((my_move_row, my_move_col, self.player_number))
                self.__send_move(my_move_row, my_move_col)
                print("Played at row {}, col {}".format(my_move_row, my_move_col))

        self.sock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', default='127.0.0.1', type=str)
    parser.add_argument('--port', default=8000, type=int)
    parser.add_argument('--name', default='chirag-ojas', type=str)
    args = parser.parse_args()

    # note: whoever connects to the server first plays first
    client = Client(args.ip, args.port, args.name)
    client.start()
    print("Game over! Winner: {}".format(client.winner))
