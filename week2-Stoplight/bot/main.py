import bot

if __name__ == "__main__":
    with open('../sample_graph_file.txt', 'r') as f:
        node_list, edge_list, color_list, start_node, end_node = bot.read_stoplight_info_file(f.read().splitlines())
        bot.stoplight_dijkstra(node_list, edge_list, color_list, start_node, end_node)
