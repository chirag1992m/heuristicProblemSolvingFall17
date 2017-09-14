table = [[[[[[0,0,0] for m in range(2)] for l in range(5)] for k in range(5)] for j in range(50)] for i in range(1001)]
N = 3
def compute():
	for stones in range(1001):
		for curMax in range(1,46):
			for reset1 in range(5):
				for reset2 in range(5):
					for lastReset in range(2):
						if(lastReset == 0):
							win = False
							move = 0
							doReset = 0
							for i in range(1,curMax + 1):
								if(table[stones-i][max(i+1,curMax)][reset2][reset1][0][0] == 0):
									win = True
									move = i
									doReset = 0
								if(win):
									break
							if(win):
								table[stones][curMax][reset1][reset2][lastReset] = [1, move, doReset]
								continue
							if(reset1 > 0):
								for i in range(1,curMax + 1):
									if(table[stones-i][max(i+1,curMax)][reset2][reset1-1][1][0] == 0):
										win = True
										move = i
										doReset = 1
									if(win):
										break
								if(win):
									table[stones][curMax][reset1][reset2][lastReset] = [1, move, doReset]
									continue
							table[stones][curMax][reset1][reset2][lastReset] = [0, 1, 0]
						else:
							move = 0
							doReset = 0
							win = False
							for i in range(1,N+1):
								if(table[stones-i][max(i+1,curMax)][reset2][reset1][0][0] == 0):
									win = True
									move = i
									doReset = 0
								if(win):
									break
							if(win):
								table[stones][curMax][reset1][reset2][lastReset] = [1, move, doReset]
								continue
							if(reset1 > 0):
								for i in range(1,N+1):
									if(table[stones-i][max(i+1,curMax)][reset2][reset1-1][1][0] == 0):
										win = True
										move = i
										doReset = 1
									if(win):
										break
								if(win):
									table[stones][curMax][reset1][reset2][lastReset] = [1, move, doReset]
									continue
							table[stones][curMax][reset1][reset2][lastReset] = [0, 1, 0]


compute()