from __future__ import print_function

import Queue
import sys

def read_stoplight_info_file(file_lines):

    # first line should be start and end node
    start_node, end_node = file_lines[0].split(' ')

    edge_list = []
    node_list = set()

    i = 1
    while i < len(file_lines):
        line = file_lines[i]
        i += 1

        if len(line.split()) > 0 and line.split(' ')[0] == 'node1':
            continue

        if len(line.split()) > 0 and line.split(' ')[0] == 'color':
            break

        if len(line.split()) > 0:
            node1, node2, color, traverse_time = line.split(' ')

            node_list.add(node1)
            node_list.add(node2)

            edge_list.append((node1, node2, color, int(traverse_time)))

    color_list = dict()
    while i < len(file_lines):
        line = file_lines[i]
        i += 1

        if len(line.split()) > 0 and line.split(' ')[0] == 'color':
            continue

        if len(line.split()) > 0:
            color, green_time, redtime = line.split(' ')

            color_list[color] = (int(green_time), int(redtime))

    return node_list, edge_list, color_list, start_node, end_node


def construct_graph(node_list, edge_list, color_list):
    graph = dict()
    for i, v in enumerate(node_list):
        graph[v] = []

    for i, v in enumerate(edge_list):
        if v[3] <= color_list[v[2]][0]:
            graph[v[0]].append((v[1], v[2], v[3]))
            graph[v[1]].append((v[0], v[2], v[3]))

    return graph


def distance_to_neighbor(current_time, neighbor, color_list):
    green_time, red_time = color_list[neighbor[1]]
    time_passed = current_time % (green_time + red_time)

    if time_passed + neighbor[2] <= green_time:
        return neighbor[2]
    else:
        return green_time + red_time - time_passed + neighbor[2]


def get_path(path_from_start, start_node, end_node):
    path = [(end_node, ('', '', ''))]

    current_node = end_node
    while current_node != start_node:
        current_node, edge = path_from_start[current_node][1], path_from_start[current_node][2]
        path.append((current_node, edge))

    return path[-1::-1]


def get_moves(full_path, color_list):
    current_time = 0
    moves = []

    for i in range(len(full_path) - 1):
        start_node, end_node = full_path[i], full_path[i+1]
        end_time = distance_to_neighbor(current_time, start_node[1], color_list) + current_time
        start_time = end_time - start_node[1][2]
        current_time = end_time

        move = [start_node[0], end_node[0], str(start_time), str(end_time)]
        moves.append(' '.join(move))

    return '\n'.join(moves)


def stoplight_dijkstra(node_list, edge_list, color_list, start_node, end_node):
    graph = construct_graph(node_list, edge_list, color_list)

    path_from_start = dict()
    for i, v in enumerate(node_list):
        path_from_start[v] = (sys.maxint, ())
    path_from_start[start_node] = (0, start_node, '')

    queue = Queue.PriorityQueue()
    queue.put((0, start_node))

    visited = set()

    while not queue.empty():
        next_vertex = queue.get()
        if next_vertex[1] in visited:
            continue

        visited.add(next_vertex[1])

        current_time = next_vertex[0]
        for neighbor in graph[next_vertex[1]]:
            dist = distance_to_neighbor(current_time, neighbor, color_list) + current_time

            if dist < path_from_start[neighbor[0]][0]:
                path_from_start[neighbor[0]] = (dist, next_vertex[1], neighbor)
                queue.put((dist, neighbor[0]))

    full_path = get_path(path_from_start, start_node, end_node)
    moves = get_moves(full_path, color_list)

    return moves
