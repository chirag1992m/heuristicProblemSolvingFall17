#!/usr/bin/python
import sys, random
from client import Client
from getopt import getopt, GetoptError
from hopcroftkarp import HopcroftKarp
import numpy
import time


"""
python3 sample_player.py -H <host> -p <port> <-c|-s>
"""

def process_file(file_data, c, k):
  """read in input file"""
  dancers = set()
  f = file_data.split("\n")
  dd = -1
  for line in f:
    tokens = line.split()
    if len(tokens) == 2:
      dancers.add((int(dd), int(tokens[0]), int(tokens[1])))
    else:
      dd += 1
  return dancers


def print_usage():
  print("Usage: python3 sample_player.py -H <host> -p <port>")


def get_args():
  host = None
  port = None
  player = None
  try:
    opts, args = getopt(sys.argv[1:], "hcsH:p:", ["help"])
  except GetoptError:
    print_usage()
    sys.exit(2)
  for opt, arg in opts:
    if opt in ("-h", "--help"):
      print_usage()
      sys.exit()
    elif opt == "-H":
      host = arg
    elif opt == "-p":
      port = int(arg)
    elif opt == "-c":
      player = "c"
    elif opt == "-s":
      player = "s"
  if host is None or port is None or player is None:
    print_usage()
    sys.exit(2)
  return host, port, player


def getDistance(point1, point2):
  return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])


def match(stars, dancers, k):
  l = 0
  h = 1000000
  for i in range(30):
    m = (l+h)/2
    # print(m)
    graph = {}
    for dancer in dancers:
      for star in stars:
        if(getDistance(star, dancer) <= m):
          if(dancer in graph):
            graph[dancer].append(star)
          else:
            graph[dancer] = []
            graph[dancer].append(star)
    res = HopcroftKarp(graph).maximum_matching()
    # print(len(res))
    if(len(res) == len(dancers)*2):
      h = m
    else:
      l = m
  return l


def get_score(stars, dancers, k, board_size, num_color):
  dd = [set() for i in range(num_color)]
  for dancer in dancers:
    dd[dancer[0]].add((dancer[1], dancer[2]))
  # print(dd[0])
  score = 0
  for col in range(num_color):
    score = max(score, match(stars, dd[col], k))
  return score

def in_dancers(dancers, x, y):
  for dancer in dancers:
    if(dancer[1] == x and dancer[2] == y):
      return True
  return False


def generate_distribution(dancers, k, board_size, num_color):
  grid = [[0 for i in range(board_size)] for j in range(board_size)]
  total = 0
  for i in range(board_size):
    for j in range(board_size):
      if(in_dancers(dancers, i, j)):
        continue
      dist = {}
      for dancer in dancers:
        if(dancer[0] not in dist):
          dist[dancer[0]] = 10000000000
        dist[dancer[0]] = min(dist[dancer[0]], getDistance((dancer[1], dancer[2]), (i,j)))
      score = 0
      for col in dist:
        score += 1/dist[col]
      # print(dist)
      grid[i][j] = score
      total += score
  points = []
  probs = []
  for i in range(board_size):
    print(grid[i])
    for j in range(board_size):
      points.append(i*board_size + j)
      probs.append(grid[i][j]/total)
  # print(probs)
  # print("")
  # print(points)
  return points, probs


# TODO add your method here
def get_stars(dancers, k, board_size, num_color):
  points, prob = generate_distribution(dancers, k, board_size, num_color)
  final_stars = set()
  best_score = 10000000000000
  start_time = time.time()
  while(time.time() - start_time < 100):
    stars = set()
    x = -1
    y = -1
    while len(stars) < k:
      pt = numpy.random.choice(points,1,False, prob)
      y = int(pt % board_size)
      pt -= y
      x = int(pt/board_size)
      if not in_dancers(dancers, x, y) and (x, y) not in stars:
        # check manhattan distance with other stars
        ok_to_add = True
        for s in stars:
          if abs(x - s[0]) + abs(y - s[1]) < num_color + 1:
            ok_to_add = False
            break
        if ok_to_add:
          stars.add((x, y))
    temp_score = get_score(stars, dancers, k, board_size, num_color)
    print(temp_score)
    if(temp_score < best_score):
      best_score = temp_score
      final_stars = stars
  stars = set()
  counter = -1
  srtd = [x for _,x in sorted(zip(prob, points))]
  srtd = srtd[::-1]
  while(len(stars) < k):
    counter += 1
    x = srtd[counter]
    y = x%board_size
    x -= y
    x = int(x/board_size)
    if not in_dancers(dancers, x, y ) and (x, y) not in stars:
      ok_to_add = True
      for s in stars:
        if abs(x - s[0]) + abs(y - s[1]) < num_color + 1:
          ok_to_add = False
          break
      if ok_to_add:
        stars.add((x, y))
  if(get_score(stars, dancers, k, board_size, num_color) < best_score):
    final_stars = stars
  stars_str = ""
  for s in final_stars:
    stars_str += (str(s[0]) + " " + str(s[1]) + " ")
  return stars_str


# TODO add your method here
def get_a_move(dancers, stars, k, board_size, num_color):
  # pick 5 random dancers from dancers
  count = 0
  moved = set()
  move = ""
  while count < 5:
    # pick random dancers
    picked = random.sample(dancers, 5 - count)
    for d in picked:
      x, y = d[0], d[1]
      if (x, y) in moved:
        continue
      c = random.sample([(1, 0), (-1, 0), (0, 1), (0, -1)], 1)[0]
      x2 = x + c[0]
      y2 = y + c[1]
      if (x2, y2) in dancers or (x2, y2) in stars:
        continue
      if x2 not in range(board_size) or y2 not in range(board_size):
        continue
      move += (str(x) + " " + str(y) + " " + str(x2) + " " + str(y2) + " ")
      dancers.remove((x, y))
      dancers.add((x2, y2))
      moved.add((x2, y2))
      count += 1
  return "5 " + move


def main():
  host, port, player = get_args()
  # create client
  client = Client(host, port)
  # send team name
  client.send("SamplePlayer")
  # receive other parameters
  parameters = client.receive()
  print(parameters)
  parameters_l = parameters.split()
  board_size = int(parameters_l[0])
  num_color = int(parameters_l[1])
  k = int(parameters_l[2]) # max num of stars
  print(board_size, num_color, k)
  # receive file data
  file_data = client.receive()
  # process file
  dancers = process_file(file_data, num_color, k) # a set of initial dancers
  print(dancers)
  print("HERE")
  # now start to play
  print(player)
  if player == "s":
    # TODO modify here
    print("getting the positions of stars")
    stars = get_stars(dancers, k, board_size, num_color)
    print(stars)
    # send stars
    client.send(stars)
  else: # choreographer
    # TODO modify here
    # receive stars from server
    stars_str = client.receive()
    stars_str_l = stars_str.split()
    stars = set()
    for i in range(int(len(stars_str_l)/2)):
      stars.add((int(stars_str_l[2*i]), int(stars_str_l[2*i+1])))
    for i in range(0, 1000): # send a thousand random moves
      move = get_a_move(dancers, stars, k, board_size, num_color)
      print(move)
      client.send(move)
    # send DONE flag
    client.send("DONE")
    # send a random line
    random_dancer = random.sample(dancers, 1)[0]
    client.send(str(random_dancer[0]) + " " + str(random_dancer[1]) + " " + str(random_dancer[0]) + " " + str(random_dancer[1] + 4))

  # close connection
  client.close()

if __name__ == "__main__":
  main()