import atexit
import argparse
from client import Client
from bot import Bot

def parse_arguments():
    parser = argparse.ArgumentParser(description='Expanding Nim Player')
    parser.add_argument('--n', dest="name", type=str, default='House Targaryen',
                        help='Name of the player')
    parser.add_argument('--f', dest="first", action="store_true",
                        help="Is it the first player?")
    parser.add_argument('--ip', type=str,
                        help='IP Address of the server', default='127.0.0.1')
    parser.add_argument('--port', type=int,
                        help='Port of the server', default=9000)

    return parser.parse_args()

def check_game_status(game_state):
    if game_state['finished']:
        print(game_state['reason'])
        exit(0)

def parse_game_stats(game_stat):
    stones = game_state['stones_left']
    current_max = game_state['current_max']
    reset_used = game_state['reset_used']

    return stones, current_max, reset_used

def default_game_stats(client):
    return client.init_stones, 3, False

if __name__ == '__main__':
    args = parse_arguments()

    print(args)

    bot = Bot()

    client = Client(args.name, args.first, (args.ip, args.port))
    atexit.register(client.close)

    bot.set_resets(client.init_resets)

    if args.first:
        stones, current_max, reset_used = default_game_stats(client)
        num_stones, reset = bot.get_move(stones, current_max, reset_used)
        check_game_status(client.make_move(num_stones, reset))
    while True:
        game_state = client.receive_move()
        check_game_status(game_state)
        stones, current_max, reset_used = parse_game_stats(game_state)
        num_stones, reset = bot.get_move(stones, current_max, reset_used)
        check_game_status(client.make_move(num_stones, reset))

