import argparse
import json
import socket
import random


class RandomBot(object):

    DATA_SIZE = 8192

    def __init__(self, name, server_address):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(server_address)
        self.__send_json({'name': name})
        self.name = name

        init_status = self.receive_init()
        self.artists_types = init_status['artists_types']
        self.required_count = init_status['required_count']
        self.auction_items = init_status['auction_items']
        self.current_wealth = init_status['init_wealth']
        self.player_count = init_status['player_count']
        self.game_state = None
        self.items_bought = [0 for _ in range(self.artists_types)]

    def __send_json(self, json_object):
        self.socket.sendall(bytes(json.dumps(json_object), 'utf-8'))

    def make_bid(self, bid_item, bid_amount):
        self.__send_json({'bid_item': bid_item, 'bid_amount': bid_amount})

    def receive_round(self):
        return json.loads(self.socket.recv(self.DATA_SIZE).decode('utf-8'))

    def receive_init(self):
        return json.loads(self.socket.recv(self.DATA_SIZE).decode('utf-8'))

    def close(self):
        self.socket.close()

    def __del__(self):
        self.close()

    def get_bid(self):
        return random.randint(0, self.current_wealth)

    def check_game_status(self):
        if self.game_state['bid_winner'] is not None:
            print('Player {} won {} on this round {} with bid amount {}.'
                  .format(self.game_state['bid_winner'],
                          self.game_state['bid_item'],
                          self.game_state['auction_round'],
                          self.game_state['winning_bid']))
            if self.game_state['bid_winner'] == self.name:
                self.current_wealth -= self.game_state['winning_bid']
                self.items_bought[int(self.game_state['bid_item'][1:])] += 1
        else:
            print('No bidders in this round {}.'.format(self.game_state['auction_round']))

        print('-------------------------------')

        if self.game_state['finished']:
            print('Game over\n{}\n'.format(self.game_state['reason']))
            return False
        return True

    def play(self):
        current_round = 0
        while True:
            bid_amt = self.get_bid()
            self.make_bid(self.auction_items[current_round], bid_amt)

            # after sending bid, wait for other player
            self.game_state = self.receive_round()
            if not self.check_game_status():
                break
            current_round += 1


if __name__ == "__main__":
    random.seed(42)

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost', type=str)
    parser.add_argument('--port', default=9000, type=int)
    parser.add_argument('--name', default='CO', type=str)
    args = parser.parse_args()

    bot = RandomBot(args.name, (args.host, args.port))
    bot.play()
