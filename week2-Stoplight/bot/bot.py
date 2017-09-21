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

def construct_graph(node_list, edge_list):
    graph = dict()
    for i, v in enumerate(node_list):
        graph[v] = []

    for i, v in enumerate(edge_list):
        graph[v[0]].append((v[1], v[2], v[3]))
        graph[v[1]].append((v[0], v[2], v[3]))

    print "Graph Constructed"
    return graph

def distance_to_neighbor(current_time, neighbor, color_list):
    green_time, red_time = color_list[neighbor[1]]
    time_passed = current_time % (green_time + red_time)

    if time_passed + neighbor[2] <= green_time:
        return neighbor[2]
    else:
        return green_time + red_time - time_passed + neighbor[2]


def stoplight_dijkstra(node_list, edge_list, color_list, start_node, end_node):
    graph = construct_graph(node_list, edge_list)

    path_from_start = dict()
    for i, v in enumerate(node_list):
        path_from_start[v] = (sys.maxint, '')
    path_from_start[start_node] = (0, start_node)

    queue = Queue.PriorityQueue(maxsize=len(node_list))
    queue.put((0, start_node))

    current_time = 0
    while not queue.empty():
        next_vertex = queue.get()
        print next_vertex

        current_time = next_vertex[0]
        for neighbor in graph[next_vertex[1]]:
            dist = distance_to_neighbor(current_time, neighbor, color_list) + current_time

            if  dist < path_from_start[neighbor[0]][0]:
                path_from_start[neighbor[0]] = (dist, next_vertex[1])
                queue.put((dist, neighbor[0]))

    print path_from_start
