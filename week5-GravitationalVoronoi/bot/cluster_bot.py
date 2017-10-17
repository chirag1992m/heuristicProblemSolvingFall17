import time
import math
import random
import argparse
import pickle
import os
from client import Client


class ClusterBot(Client):

    def __init__(self, host, port, name):
        self.pre_calculate_clusters()
        super().__init__(host, port, name)
        self.cluster = self.load_clusters(self.num_stone)
        self.current_move = 0

    @staticmethod
    def load_clusters(num_stones):
        return pickle.load(open('cluster_bot_precomputed_{}.pkl'.format(num_stones), 'rb'))

    @staticmethod
    def pre_calculate_clusters():
        for k in range(1, 13):
            file_name = 'cluster_bot_precomputed_{}.pkl'.format(k)
            if os.path.exists(file_name):
                continue
            clusters = ClusterBot.compute_clusters(k)
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
                        cur_dist = ClusterBot.euclidean(centroids[l], [i, j])
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

    def get_closest_valid_point(self, move_row, move_col):
        radius = 1
        tries = 0
        while True:
            new_move_row = random.randint(max(0, move_row-radius),
                                          min(self.grid_size - 1, move_row+radius))
            new_move_col = random.randint(max(0, move_col-radius),
                                          min(self.grid_size - 1, move_col+radius))
            if self._Client__is_valid_move(new_move_row, new_move_col):
                break
            tries += 1
            if tries > 3:
                radius *= 2
                tries = 0
        return new_move_row, new_move_col

    def get_move(self):
        move_row, move_col = self.cluster[self.current_move]
        if not self._Client__is_valid_move(move_row, move_col):
            move_row, move_col = self.get_closest_valid_point(move_row, move_col)
        self.current_move += 1
        return move_row, move_col


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', default='127.0.0.1', type=str)
    parser.add_argument('--port', default=8000, type=int)
    parser.add_argument('--name', default='chirag-ojas', type=str)
    args = parser.parse_args()

    client = ClusterBot(args.ip, args.port, args.name)
    client.start()
    print("Game over! Winner: {}".format(client.winner))
