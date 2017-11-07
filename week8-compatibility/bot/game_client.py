import argparse
from urllib.parse import urlencode
import requests
from datetime import datetime, timedelta
import json
import random


class GameClient(object):
    def __init__(self,
                 server_address,
                 server_port,
                 player_role,
                 player_name,
                 game_params):
        self.base = 'http://' + server_address + ':' + str(server_port) + '/api/'
        self.player_role = player_role
        self.player_name = player_name
        if 'access_code' in game_params:
            self.access_code = game_params['access_code']
            self.game_id = game_params['game_id']
            self.problem_id = game_params['problem_id']
        else:
            self.start(game_params['packages'],
                       game_params['versions'],
                       game_params['pairs'])
        self.parameters, self.pairs = self.parse_problem(self.get_problem())

    def play_as_solver(self):
        self.player_role = 'solver'
        self.register_game(self.player_name + self.player_role)
        self.parameters, self.pairs = self.parse_problem(self.get_problem())
        self.play()

    def start(self, num_packages, num_versions, num_compatibilities):
        self.create_game(num_packages, num_versions, num_compatibilities)
        self.register_game(self.player_name)
        self.problem_id = self.player_name

    def make_request(self, api_name, params, body=None):
        try:
            url = self.base + api_name + '?' + urlencode(params)
            if body:
                response = requests.post(url, data=body)
            else:
                response = requests.get(url)
            response = json.loads(response.content)
            print(response)
            if response['success']:
                return response
            else:
                print("Some error with server: {}".format(response['msg']))
                exit()
        except Exception as e:
            print(e)
            exit()

    def create_game(self, num_packages, num_versions, num_compatibilities,
                    now=datetime.now(),
                    poser_deadline=datetime.now()+timedelta(hours=1),
                    solver_deadline=datetime.now()+timedelta(hours=2)):
        time_format = "%m/%d/%Y %I:%M %p"
        params = {
            'date1': now.strftime(time_format),
            'date2': poser_deadline.strftime(time_format),
            'date3': solver_deadline.strftime(time_format),
            'numpackages': num_packages,
            'numversions': num_versions,
            'numcompatibles': num_compatibilities
        }
        response = self.make_request('create', params)
        if response:
            self.game_id = response['id']
        else:
            print("Couldn\'t create game. Exiting!")
            exit()

    def register_game(self, player_id):
        params = {
            'id': self.game_id,
            'name': player_id
        }
        response = self.make_request('register', params)
        if response:
            self.access_code = response['code']
        else:
            print("Can\'t register player! Exiting!")
            exit()

    def get_problem(self):
        params = {
            'id': self.game_id,
            'pid': self.problem_id,
            'role': self.player_role,
            'code': self.access_code
        }
        response = self.make_request('get', params)
        if response:
            problem = response['data']
            return problem
        else:
            print("Can\'t get problem! Exiting!")
            exit()

    def parse_problem(self, problem):
        parameters = []
        pairs = []
        if self.player_role == 'poser':
            problem = problem.split('\n')[0]
            parameters = tuple(map(int, problem.split(' ')))
        elif self.player_role == 'solver':
            # print(problem)
            problem = problem.split('\n')
            parameters = tuple(map(int, problem[0].split(' ')))
            for i in range(1, len(problem) - 1):
                p1, v1, p2, v2 = tuple(map(int, problem[i].split()))
                pairs.append(((p1, v1), (p2, v2)))
        else:
            print("Wrong player role {}! Exiting!".format(self.player_role))
        return {
                   'packages': parameters[0],
                   'versions': parameters[1],
                   'compatibilities': parameters[2]
        }, pairs

    def submit_solution(self, solution):
        params = {
            'id': self.game_id,
            'pid': self.problem_id,
            'role': self.player_role,
            'code': self.access_code
        }
        payload = {'data': solution}
        response = self.make_request('submit', params, payload)
        if not response:
            print("Can\'t submit solution! Exiting!")
            exit()

    def poser(self):
        pairs = []
        valid_configurations = []
        return pairs, valid_configurations

    def solver(self):
        valid_configurations = []
        return valid_configurations

    @staticmethod
    def choose_best_config(configs):
        maximal = configs[0]
        found = False
        for idx in range(1, len(configs)):
            if GameClient.is_bigger(configs[idx], maximal):
                maximal = configs[idx]
                found = True
        return [maximal]

    @staticmethod
    def is_incomparable(config1, config2):
        small, big = False, False
        for x1, x2 in zip(config1, config2):
            if x1 < x2:
                small = True
            if x1 > x2:
                big = True
        return big and small

    @staticmethod
    def is_equal(config1, config2):
        for x1, x2 in zip(config1, config2):
            if x1 != x2:
                return False
        return True

    @staticmethod
    def is_bigger(config1, config2):
        bigger = False
        for x1, x2 in zip(config1, config2):
            if x1 < x2:
                return False
            if x1 > x2:
                bigger = True
        return bigger

    def play(self):
        if self.player_role == 'poser':
            print("Running Poser...")
            self.pairs, configurations = self.poser()
            string_builder = [str(len(self.pairs))]
            for pair in self.pairs:
                p1 = ' '.join(map(str, pair[0]))
                p2 = ' '.join(map(str, pair[1]))
                string_builder.append(' '.join([p1, p2]))
            string_builder.append(str(len(configurations)))
            for conf in configurations:
                string_builder.append(' '.join(map(str, conf)))
            to_send = '\n'.join(string_builder)
            print(to_send)
            self.submit_solution(to_send)
        elif self.player_role == 'solver':
            print("Running Solver...")
            configurations = self.solver()
            string_builder = [str(len(configurations))]
            for conf in configurations:
                string_builder.append(' '.join(map(str, conf)))
            to_send = '\n'.join(string_builder)
            print(to_send)
            self.submit_solution(to_send)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost', type=str)
    parser.add_argument('--port', default=34567, type=int)
    parser.add_argument('--player', default='both', type=str)
    parser.add_argument('--problem-id', default=None, type=str)
    parser.add_argument('--game-id', default=None, type=int)
    parser.add_argument('--access-code', default=None, type=int)
    parser.add_argument('--packages', default=1, type=int)
    parser.add_argument('--versions', default=1, type=int)
    parser.add_argument('--pairs', default=1, type=int)

    args = parser.parse_args()
    if args.game_id and args.access_code:
        client = GameClient(args.host, args.port,
                            args.player, 'CO',
                            {'game_id': args.game_id,
                             'access_code': args.access_code,
                             'problem_id': args.problem_id})
        client.play()
    elif args.player == 'both':
        client = GameClient(args.host, args.port,
                            'poser', 'CO',
                            {'packages': args.packages,
                             'versions': args.versions,
                             'pairs': args.pairs})
        client.play()
        client.play_as_solver()
    else:
        client = GameClient(args.host, args.port,
                            args.player, 'CO',
                            {'packages': args.packages,
                             'versions': args.versions,
                             'pairs': args.pairs})
        client.play()
