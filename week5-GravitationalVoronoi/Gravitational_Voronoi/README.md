# Gravitational Voronoi

This repository contains the architect code for Gravitational Voronoi. It consists of a game server, a sample client, and a web visualization interface that displays the game progress in real time. Currently, the visualization interface is not working properly, but a fix will be pushed shortly.

## The server

The server is written in Python 3. To run the server, execute:

```
python3 voronoi_game.py <number-of-stones> <number-of-players> <host-ip> <port>
```

Note that ports 10000 and 8080 are reserved for the web interface, so please use some other port. After all clients have connected, press `<Enter>` to start the game.

The server calculates the area of influence of each player discretely on a 1000 by 1000 grid. The final score of each player is the number of cells under the influence of that player.

## The client

In our implementation, there is no flag that indicates which client is the first (or second) player. Rather, player order is determined by the order in which each client connects to the server, i.e., the first client that connects to the server becomes the first player of the game.

A sample client in Python 3 is provided. To run the sample client, execute:

```
python3 voronoi_client.py <server-ip> <port> <team-name>
```

If you wish to write your own client, please follow the server-client communication protocol:

1. Connect your client to the server.

2. Receive game information. After connecting your client to the server, you should receive the game information from the server in the format of `"<number-of-players> <number-of-stones>\n"`. The string is delimited by a space and ends with a new line character.

3. Send team name. After receiving the game information, you should send your team name to the server as a string.

4. Receive game updates. Your client will receive an update from the server when it is your turn. The update consists of three parts.
   1. Game over flag. The flag is set to `1` when the game is over, and `0` otherwise
   2. Scores. Say there are N players. Then there will be N numbers, representing the score from player 1 to player N.
   3. New moves. These are the moves that have been played after you played your last move. Each move consists of three numbers: the row of the move, the column of the move, and the player than made the move. The moves are ordered in the order in which they were played.

Notice that every number in the game update is separated by a space, and at the very end there will be a new line character.

The following represents what a general game update looks like. Note that the move row and move columns are **0-indexed**, and move players are **1-indexed**.

```
"<game-over-flag> <score1> <score2> ... <move1-row> <move1-col> <move1-player> <move2-row> <move2-col> <move2-player> ...\n"
```

5. Send move to server. After receiving a game update from the server, your client should finish your turn by sending a move to the server. The move should simply be a string `"<move_row> <move_col>"` - row and column of the move separated by a space.

## Running the game without display

To run the game without the display, run the server with:

```
python3 voronoi_game.py <number-of-stones> <number-of-players> <host-ip> <port>
```

and run each client with (if you are using the client provided here):

```
python3 voronoi_client.py <server-ip> <port> <team-name>
```

Finally, press `<Enter>` in the server terminal to start the game.

## Running the game with display

Coming soon
