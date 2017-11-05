from urllib.parse import urlencode
from urllib.request import Request, urlopen
from datetime import datetime, timedelta
import json


class GameClient(object):
    def __init__(self,
                 server_address,
                 server_port,
                 player_role,
                 player_name,
                 game_params):
        self.base = 'http://' + server_address + ':' + str(server_port) + '/api/'
        self.player_role = player_role
        self.player_id = player_name
        if 'access_code' in game_params:
            self.access_code = game_params['access_code']
            self.game_id = game_params['game_id']
        else:
            self.start(game_params['packages'],
                       game_params['versions'],
                       game_params['pairs'])
        self.parameters, self.pairs = self.parse_problem(self.get_problem())

    def start(self, num_packages, num_versions, num_compatibilities):
        self.create_game(num_packages, num_versions, num_compatibilities)
        self.register_game()

    def make_request(self, api_name, params, body=None):
        try:
            url = self.base + api_name + '?' + urlencode(params)
            req = Request(url=url,
                          method='GET' if body is None else 'POST',
                          data=body if body is None else body.encode('ascii'))
            with urlopen(req) as response:
                the_page = response.read()
                return json.loads(the_page.decode())
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

    def register_game(self):
        params = {
            'id': self.game_id,
            'name': self.player_id
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
            'pid': self.player_id,
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
            parameters = problem.split(' ')
        elif self.player_role == 'solver':
            problem = problem.split('\n')
            parameters = problem[0].split(' ')
            for i in range(1, len(problem)):
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
            'pid': self.player_id,
            'role': self.player_role,
            'code': self.access_code
        }
        response = self.make_request('submit', params, solution)
        if response:
            print(response)
        else:
            print("Can\'t submit solution! Exiting!")
            exit()

    def poser(self):
        pairs = []
        valid_configurations = []
        return pairs, valid_configurations

    def solver(self):
        valid_configurations = []
        return valid_configurations

    def play(self):
        if self.player_role == 'poser':
            self.pairs, configurations = self.poser()
            string_builder = [str(len(self.pairs))]
            for pair in self.pairs:
                p1 = ' '.join(pair[0])
                p2 = ' '.join(pair[1])
                string_builder.append(' '.join([p1, p2]))
            string_builder.append(str(len(configurations)))
            for conf in configurations:
                string_builder.append(' '.join(conf))
            self.submit_solution('\n'.join(string_builder))
        elif self.player_role == 'solver':
            configurations = self.solver()
            string_builder = [str(len(configurations))]
            for conf in configurations:
                string_builder.append(' '.join(conf))
            self.submit_solution('\n'.join(string_builder))


if __name__ == "__main__":
    client = GameClient('localhost', 34567,
                        'poser', 'CO',
                        {'packages': 1,
                         'versions': 1,
                         'pairs': 10})
    client.play()
