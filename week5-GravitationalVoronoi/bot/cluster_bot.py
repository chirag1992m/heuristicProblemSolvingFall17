import time
import math
import random
import argparse
from .client import Client


class ClusterBot(Client):

    def __init__(self, host, port, name):
        super().__init__(host, port, name)
        self.cluster = self.compute_clusters()
        self.current_move = 0

    @staticmethod
    def euclidean(point1, point2):
        distance = (point1[0] - point2[0]) * (point1[0] - point2[0])
        distance += (point1[1] - point2[1]) * (point1[1] - point2[1])
        return math.sqrt(distance)

    def compute_clusters(self):
        start_time = time.time()
        k = self.num_stone
        centroids = [[random.randint(0, 999), random.randint(0, 999)] for _ in range(k)]
        points = [[] for _ in range(k)]
        last = []
        turns = 0
        while last != centroids:
            if turns > 10:
                break
            turns += 1
            last = centroids
            # reorganize
            for i in range(1000):
                for j in range(1000):
                    index = -1
                    closest_dist = 2000
                    for l in range(k):
                        cur_dist = self.euclidean(centroids[l], [i, j])
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
        print("Took {} time to compute centroids.".format(time.time() - start_time))
        return centroids

    def get_move(self):
        to_ret = self.cluster[self.current_move]
        self.current_move += 1
        return to_ret


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', default='locahost', type=str)
    parser.add_argument('--port', default=8000, type=int)
    parser.add_argument('--name', default='chirag-ojas', type=str)
    args = parser.parse_args()

    host = args.ip
    port = args.port
    name = args.name
    client = ClusterBot(host, port, name)
    client.start()
