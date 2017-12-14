# Self-Play bots for Tic-Tac-Toe

Based on the paper by DeepMind papers:
1. [Mastering the game of Go without human knowledge](http://nature.com/articles/doi:10.1038/nature24270)
2. [Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm
](https://arxiv.org/abs/1712.01815)

This is an attempt to make bots to perfectly play Tic-Tac-Toe and 
Connect Four just by playing with itself and constantly improving.

From 10000 feet, the cycle of improvement looks like:
1. Start from Randomly Initialised Model
2. Generate Training Data by Self-Play Game Simulations using
    Monte-Carlo Tree-Search (MCTS)
3. Train the model on the generated data
4. Evaluate/Benchmark the new model with the best model available
5. Choose the best model and checkpoint it
6. Repeat from step-2. The training stops when the model stops
    improving.

### Requirements:

- Python >= 3.5
- [Gym-RING](https://github.com/chirag1992m/gym/tree/RING)
- [PyTorch](http://pytorch.org/)
- [NetworkX](https://github.com/networkx/networkx)
- numpy

### How to train and run?

#### Tic Tac Toe
To train the network and then play with the bot:

```commandline
cd <repo_root>/week11-Project/
python -m TicTacToe.train_agent

python -m TicTacToe.play
```

#### Connect Four
To train the network and then play with the bot:

```commandline
cd <repo_root>/week11-Project/
python -m ConnectFour.train_agent

python -m ConnectFour.play
```

