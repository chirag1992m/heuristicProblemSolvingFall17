import argparse
import random
import time

from .random_bot import RandomBot


class ValueBot(RandomBot):
    DATA_SIZE = 8192

    def __init__(self, name, server_address):
        super(ValueBot, self).__init__(name, server_address)

        self.player_paintings = dict()
        self.player_wealths = dict()
        self.required_paintings = dict()
        self.paintings_queue = self.auction_items
        self.paintings_value = None
        self.players_focus = dict()

        name = self.name
        self.player_paintings[name] = [0 for _ in range(self.artists_types)]
        self.player_wealths[name] = self.init_status['init_wealth']
        self.required_paintings[name] = [self.required_count
                                         for _ in range(self.artists_types)]
        self.players_focus[name] = None
        self.wealth_distribution = None
        self.to_redistribute = False

    def redistribute_wealth(self):
        required = self.required_paintings[self.name][self.players_focus[self.name]]
        if required == 1:
            self.wealth_distribution = [self.current_wealth]
        elif required == 2:
            x = int(self.current_wealth * 0.6)
            y = self.current_wealth - x
            self.wealth_distribution = [x, y]
        else:
            middle = (required // 2, 0.5)
            start = (0, 1.0)
            end = (required - 1, 0.75)
            m1 = (middle[1] - start[1]) / (middle[0] - start[0])
            m2 = (end[1] - middle[1]) / (end[0] - middle[0])
            self.wealth_distribution = []
            for i in range(middle[0]):
                y = (m1 * (i - start[0])) + start[1]
                self.wealth_distribution.append(y)
            for i in range(middle[0], end[0] + 1):
                y = (m2 * (i - middle[0])) + middle[1]
                self.wealth_distribution.append(y)
            total = 0
            s = sum(self.wealth_distribution)
            for i in range(len(self.wealth_distribution)):
                y = int(self.current_wealth * self.wealth_distribution[i] / s)
                total += y
                self.wealth_distribution[i] = y
            if total < self.current_wealth:
                self.wealth_distribution[0] += self.current_wealth - total
            elif total > self.current_wealth:
                self.wealth_distribution[-1] -= total - self.current_wealth

    def get_focus(self):
        name = self.name
        # Check competitors
        competitors = []
        for player in self.players_focus.keys():
            if player == name:
                continue
            if self.players_focus[player] == self.players_focus[name]:
                competitors.append(player)
        for competitor in competitors:
            if self.player_wealths[competitor] > self.player_wealths[name]:
                # He has more money. What should we do?
                if (self.required_paintings[competitor][self.players_focus[competitor]] >=
                        self.required_paintings[name][self.players_focus[name]]):
                    continue
                # he can probably kill us
                return True
            else:
                # haha you fucker. I am gonna beat you to death!
                continue
        return False

    def value(self):
        self.paintings_value = dict()
        forget = None
        change_focus = (False, -1)
        for player in self.player_paintings.keys():
            self.paintings_value[player] = [0.0 for _ in range(self.artists_types)]
            for i in range(self.artists_types):
                required = self.required_paintings[player][i]
                if required == 0:
                    print("Forgetting player {}".format(player))
                    forget = player
                    continue
                if required == 1 and player == self.name:
                    change_focus = (True, i)
                self.paintings_value[player][i] += 1.0 / required
                plays_required = 0
                for painting in self.paintings_queue:
                    if required <= 0:
                        break
                    plays_required += 1
                    if int(painting[1:]) == i:
                        required -= 1
                if required <= 0:
                    self.paintings_value[player][i] += 1.0 / plays_required
                else:
                    self.paintings_value[player][i] = 0.0
        if forget and forget != self.name:
            self.player_paintings.pop(forget, None)
            self.player_wealths.pop(forget, None)
            self.required_paintings.pop(forget, None)
            self.players_focus.pop(forget, None)
        if forget == self.name:
            print("Game should have finished!!!!")
            exit()
        name = self.name
        if self.players_focus[name] is None:
            # take the second max, let the people catch the low hanging fruit
            # and we'll focus on the upper fruit
            to_focus = 1
            if self.player_count == 2:
                to_focus = 0
            self.players_focus[name] = self.paintings_value[name].index(sorted(
                self.paintings_value[name],
                reverse=True)[to_focus])
            print("Starting with focus {}".format(self.players_focus[name]))
            self.redistribute_wealth()
            return
        if change_focus[0]:
            if (self.players_focus[name] != change_focus[1] and
                        self.required_paintings[name][self.players_focus[name]] > 1):
                print("We randomly got some great paintings....")
                self.players_focus[name] = change_focus[1]
                self.redistribute_wealth()
                return
        change = False
        old_focus = self.players_focus[name]
        try:
            counter = 0
            while self.get_focus():
                self.players_focus[name] = self.paintings_value[name].index(sorted(
                    self.paintings_value[name],
                    reverse=True)[counter])
                counter += 1
                change = True
            if change:
                print("Changed focus from {} to {}".format(old_focus, self.players_focus[name]))
        except Exception:
            self.players_focus[name] = old_focus
            change = False

        if change:
            self.redistribute_wealth()

    def get_bid(self):
        self.value()
        to_return = 0
        if self.players_focus[self.name] == int(self.paintings_queue[0][1:]):
            required = self.required_paintings[self.name][self.players_focus[self.name]]
            to_return = self.wealth_distribution[-required]
        print(self.required_paintings, self.players_focus, self.wealth_distribution)
        if to_return == 0:
            # check if someone else is winning. Don't let them win!
            for player in self.player_wealths:
                if player == self.name:
                    continue
                if (self.required_paintings[player][self.players_focus[player]] == 1
                    and self.players_focus[player] == int(self.paintings_queue[0][1:])):
                    required_wealth = self.required_paintings[self.name][
                                          self.players_focus[self.name]] * 2
                    left_wealth = max(0, self.current_wealth - required_wealth)
                    to_return = min(self.player_wealths[player] + 1, left_wealth)
                    print("Tried to kick someone!")
                    self.to_redistribute = True
                    time.sleep(5)
        print("Bidding {} on {} with left {}".format(to_return, self.paintings_queue[0],
                                                     self.current_wealth))
        return to_return

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
            # Update paintings
            name = self.game_state['bid_winner']
            if name not in self.player_paintings:
                self.player_paintings[name] = [0 for _ in range(self.artists_types)]
            for player in self.player_paintings:
                if name != self.name:
                    self.players_focus[player] = self.player_paintings[player].index(max(
                        self.player_paintings[player]))
            self.player_paintings[name][int(self.game_state['bid_item'][1:])] += 1
            if name not in self.player_wealths:
                self.player_wealths[name] = self.init_status['init_wealth']
            self.player_wealths[name] -= self.game_state['winning_bid']
            if name not in self.required_paintings:
                self.required_paintings[name] = [self.required_count
                                                 for _ in range(self.artists_types)]
            self.required_paintings[name][int(self.game_state['bid_item'][1:])] -= 1
            del self.paintings_queue[0]
            if self.to_redistribute and self.game_state['bid_winner'] == self.name:
                self.redistribute_wealth()
            self.to_redistribute = False
        else:
            print('No bidders in this round {}.'.format(self.game_state['auction_round']))

        print('-------------------------------')

        if self.game_state['finished']:
            print('Game over\n{}\n'.format(self.game_state['reason']))
            return False
        return True


if __name__ == "__main__":
    random.seed(42)

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost', type=str)
    parser.add_argument('--port', default=9000, type=int)
    parser.add_argument('--name', default='CO', type=str)
    args = parser.parse_args()

    bot = ValueBot(args.name, (args.host, args.port))
    bot.play()
