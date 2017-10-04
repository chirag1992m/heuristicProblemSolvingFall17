from __future__ import print_function

# Echo client program
import socket
import sys
# import random

HOST = sys.argv[1].split(":")[0]
PORT = int(sys.argv[1].split(":")[1])              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
myWeight = dict()

first = 0
name = "ojas-chirag"

for idx, val in enumerate(sys.argv):
    if(val == "-f"): 
        first = 1
    if(val == "-n"):
        name = sys.argv[idx + 1]
s.sendall('{} {}'.format(name, first))


k = int(s.recv(1024))
print("Number of Weights is: " + str(k))

for i in range(1, k):
    myWeight[i] = 1;


def calcTorque1(board):
    torque1 = 3*3
    for i in range(61):
        torque1 += board[i]*(i-27)
    return torque1


def calcTorque2(board):
    torque2 = -3*1
    for i in range(61):
        torque2 += board[i]*(29 - i)
    return torque2


def check_balance(board):
    left_torque = 0
    right_torque = 0
    for i in range(0,61):
        left_torque += (i - 30 + 3) * board[i]
        right_torque += (i - 30 + 1) * board[i]
    left_torque += 3 * 3
    right_torque += 1 * 3
    return left_torque >= 0 and right_torque <= 0


def find_place_position(key, board):
    for i in range(0,61):
        if board[i] == 0:
            board[i] = key
            if check_balance(board):
                board[i] = 0
                return i
            board[i] = 0
    return -100


def addition(board, weights):
    torque1 = calcTorque1(board)
    torque2 = calcTorque2(board)
    t1 = 100000000000
    t2 = 100000000000
    w1 = -1
    p1 = -1
    for move in sorted(weights, reverse = True):
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
    print("Placing weight ", w1, " at position ", p1-30)
    weights.remove(w1)
    board[p1] = w1
    return (w1, p1 - 30)


def change1(pos, weight):
    return weight*(pos - 27)


def change2(pos, weight):
    return weight*(29 - pos)


def remove(board, stonesLeft):
    torque1 = calcTorque1(board)
    torque2 = calcTorque2(board)
    # print(board)
    if(stonesLeft < 7):
        for k in range(61):
            if(board[k] != 0):
                temp = board[k]
                board[k] = 0
                temp1 = torque1 - change1(k, board[k])
                temp2 = torque2 - change2(k, board[k])
                if(temp1 >= 0 and temp2 >= 0 and dfs(board) == 0):
                    torque1  = temp1
                    torque2 = temp2
                    print("Removing from position ", k-30)
                    return k-30
                else:
                    board[k] = temp
    tt = 10000000000
    pos = -1
    for k in range(61):
        if(board[k] != 0):
            if(torque1 >= change1(k, board[k]) and torque2 >= change2(k, board[k])):
                boardvalue = board[k]
                board[k] = 0
                temp = torque1 - change1(k, board[k])
                temp += torque2 - change2(k, board[k])
                if(temp < tt):
                    tt = temp
                    pos = k
                board[k] = boardvalue
    if(pos != -1):
        board[pos] = 0
        print("Removing from position " , pos-30)
        return pos - 30
    for k in range(61):
        if(board[k] != 0):
            if(torque1 >= change1(k, board[k]) and torque2 >= change2(k, board[k])):
                board[k] = 0
                print("Removing from position ", k-30)
                return k - 30
    for k in range(61):
        if(board[k] != 0):
            board[k] = 0
            print("Removing from position ", k-30)
            return k-30


def dfs(bd):
    torque1 = calcTorque1(board)
    torque2 = calcTorque2(board)
    for k in range(61):
        if(bd[k] != 0):
            temp = bd[k]
            bd[k] = 0
            temp1 = torque1 - change1(k, bd[k])
            temp2 = torque2 - change2(k, bd[k])
            if(torque1 >= 0 and torque2 >= 0 and dfs(bd) == 0):
                bd[k] = temp
                return 1
            bd[k] = temp
    return 0


stonesLeft = k
weights = list(range(1, k+1))
while True:
    data = s.recv(1024)
    while not data:
        continue
    data = [int(data.split(' ')[i]) for i in range(0, 63)]
    board = data[1:-1]
    check_balance(board)
    #print board
    if data[62] == 1:
        break

    if data[0] == 0:
        choice = addition(board, weights)
        s.sendall('{} {}'.format(choice[0], choice[1]))

    else:
        choice = remove(board, stonesLeft)
        stonesLeft -= 1
        s.sendall('{}'.format(choice))


s.close()
