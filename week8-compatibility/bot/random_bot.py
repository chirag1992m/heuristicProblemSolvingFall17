import argparse
from .game_client import GameClient
import random


class RandomBot(GameClient):
    def __init__(self,
                 server_address,
                 server_port,
                 player_role,
                 player_name,
                 game_params):
        super(RandomBot, self).__init__(server_address,
                                        server_port,
                                        player_role,
                                        player_name,
                                        game_params)
        random.seed(42)

    def poser(self):
        # randomly generate X number of pairs and a configuration
        for i in range(random.randint(1, self.parameters['compatibilities'])):
            p1 = random.randint(1, self.parameters['packages'])
            v1 = random.randint(1, self.parameters['versions'])
            p2 = random.randint(1, self.parameters['packages'])
            v2 = random.randint(1, self.parameters['versions'])
            self.pairs.append(((p1, v1), (p2, v2)))
        configuration = []
        for i in range(1, self.parameters['packages'] + 1):
            p = i
            v = random.randint(1, self.parameters['versions'])
            configuration.append((p, v))
        return self.pairs, configuration

    def solver(self):
        configuration = []
        for pair in self.pairs:
            choice = random.randint(1, 3)
            if choice == 1:
                configuration.append(pair[0])
            elif choice == 2:
                configuration.append(pair[1])
            else:
                continue
        return configuration


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost', type=str)
    parser.add_argument('--port', default=34567, type=int)
    parser.add_argument('--player', default='both', type=str)
    parser.add_argument('--game-id', default=None, type=int)
    parser.add_argument('--access-code', default=None, type=str)
    parser.add_argument('--packages', default=2, type=int)
    parser.add_argument('--versions', default=3, type=int)
    parser.add_argument('--pairs', default=5, type=int)

    args = parser.parse_args()
    if args.game_id and args.access_code:
        client = RandomBot(args.host, args.port,
                           args.player, 'CO',
                           {'game_id': args.game_id,
                            'access_code': args.access_code})
    elif args.player == 'both':
        client = RandomBot(args.host, args.port,
                           'poser', 'CO',
                           {'packages': args.packages,
                            'versions': args.versions,
                            'pairs': args.pairs})
        client.play()
        client.set_player('solver')
        client.play()
    else:
        client = RandomBot(args.host, args.port,
                           args.player, 'CO',
                           {'packages': args.packages,
                            'versions': args.versions,
                            'pairs': args.pairs})
