import argparse
from client import Client
import bot
import pickle


def parse_arguments():
    parser = argparse.ArgumentParser(description='Stoplight Shortest Path Player')
    parser.add_argument('--ip', type=str,
                        help='IP Address of the server', default='127.0.0.1')
    parser.add_argument('--port', type=int,
                        help='Port of the server', default=12345)

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    client = Client(args.ip, args.port)

    file_text = client.recv_stoplight()
    node_list, edge_list, color_list, start_node, end_node = bot.read_stoplight_info_file(file_text.split('\n'))
    moves_string = bot.stoplight_dijkstra(node_list, edge_list, color_list, start_node, end_node)
    client.send_resp(moves_string)

    pickle.dump((file_text, moves_string), open("game_file.pkl", 'wb'))
