import time
import math
import random
import argparse
import pickle
import os
from .client import Client


class ClusterBot2(Client):

    def __init__(self, host, port, name):
        self.pre_calculate_clusters()
        super().__init__(host, port, name)
        self.cluster = self.load_clusters(self.num_stone)
        self.current_move = 0
        self.used_clusters = [0 for i in range(self.num_stone)]

    def reset(self):
        self.cluster = self.load_clusters(self.num_stone)
        self.current_move = 0
        self.used_clusters = [0 for i in range(self.num_stone)]
        self.grid = [[0] * self.grid_size for _ in range(self.grid_size)]
        self.moves = []
        print("everything cleared!")

    @staticmethod
    def load_clusters(num_stones):
        return pickle.load(open('./bot/cluster_bot_precomputed_{}.pkl'.format(num_stones), 'rb'))

    @staticmethod
    def pre_calculate_clusters():
        for k in range(1, 13):
            file_name = './bot/cluster_bot_precomputed_{}.pkl'.format(k)
            if os.path.exists(file_name):
                continue
            clusters = ClusterBot2.compute_clusters(k)
            pickle.dump(clusters, open(file_name, 'wb'))

    @staticmethod
    def euclidean(point1, point2):
        distance = (point1[0] - point2[0]) * (point1[0] - point2[0])
        distance += (point1[1] - point2[1]) * (point1[1] - point2[1])
        return math.sqrt(distance)

    @staticmethod
    def compute_clusters(k):
        centroids = [[random.randint(0, 999), random.randint(0, 999)] for _ in range(k)]
        points = [[] for _ in range(k)]
        last = []
        total_time = 450 * k
        start_time = time.time()
        while last != centroids:
            if time.time() - start_time > total_time:
                break
            last = centroids
            # reorganize
            for i in range(1000):
                for j in range(1000):
                    index = -1
                    closest_dist = 2000
                    for l in range(k):
                        cur_dist = ClusterBot2.euclidean(centroids[l], [i, j])
                        if cur_dist < closest_dist:
                            closest_dist = cur_dist
                            index = l
                    points[index].append([i, j])
            new_clusters = [[0, 0] for _ in range(k)]
            for l in range(k):
                for point in points[l]:
                    new_clusters[l][0] += point[0]
                    new_clusters[l][1] += point[1]
                new_clusters[l][0] /= len(points[l])
                new_clusters[l][1] /= len(points[l])
                new_clusters[l][0] = int(new_clusters[l][0])
                new_clusters[l][1] = int(new_clusters[l][1])
            centroids = new_clusters
        return centroids

    def get_next_move(self):
        radius = 1
        tries = 0
        while True:
            for i in range(self.num_stone):
                if self.used_clusters[i] == 0:
                    move_row, move_col = self.cluster[i]
                    new_move_row = random.randint(max(0, move_row-radius),
                                                  min(self.grid_size - 1, move_row+radius))
                    new_move_col = random.randint(max(0, move_col-radius),
                                                  min(self.grid_size - 1, move_col+radius))
                    if self._Client__is_valid_move(new_move_row, new_move_col):
                        self.used_clusters[i] = 1
                        return new_move_row, new_move_col

            tries += 1
            if tries > 5:
                radius *= 2
                tries = 0

    def get_move(self):
        return self.get_next_move()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', default='127.0.0.1', type=str)
    parser.add_argument('--port', default=8000, type=int)
    parser.add_argument('--name', default='chirag-ojas', type=str)
    args = parser.parse_args()

    client = ClusterBot2(args.ip, args.port, args.name)
    client.start()
    print("Game over! Winner: {}".format(client.winner))
