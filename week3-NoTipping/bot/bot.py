torque1 = 6
torque2 = 6

players = [[i for i in range(25)] for j in range(2)]

board = [0 for i in range(61)]
board[26] = 3   # corresponds to -4 position


def addition():
    t1 = 100000000000
    t2 = 100000000000
    w1 = -1
    p1 = -1
    for move in sorted(players[0], reverse = True):
        for k in range(61):
            if(board[k] == 0):
                temp_t1 = torque1
                temp_t2 = torque2
                if(k < 27):
                    temp_t1 -= move*(27 - k)
                else:
                    temp_t1 += move*(k - 27)
                if(k < 29):
                    temp_t2 += move*(29 - k)
                else:
                    temp_t2 -= move*(k - 29)
                if(temp_t1 >=0 and temp_t2 >= 0):
                    if(temp_t1 < t1 and temp_t2 < t2):
                        t1 = temp_t1
                        t2 = temp_t2
                        w1 = move
                        p1 = k
                        break
    print("Placing weight ", w1, " at position ", k-30)
    players[0].remove(w1)
    board[k] = w1
    torque1 = t1
    torque2 = t2

def remove():
    for k in range(61):
        if(board[k] != 0):
            temp = board[k]
            board[k] = 0
            if(dfs(board)):
                print("Removing from position ", k)
            else:
                board[k] = temp
def dfs(bd):
    for k in range(61):
        if(bd[k] != 0):
            temp = bd[k]
            bd[k] = 0
            if(dfs(bd) == 0):
                return 1
            bd[k] = temp
    return 0
