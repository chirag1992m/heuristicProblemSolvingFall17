import pickle


def make_moves_table():
    return []


def main():
    table = make_moves_table()
    pickle.dump(table, open("moves_table.pkl", "wb"))


if __name__ == "__main__":
    main()