# Auction Game

## Description

A sealed bid auction will take place. In the auction, there are k artists. Each of p players wants to obtain n works of one artist -- any artist is fine -- before anyone else does.

All players start out with 100 units of money. The artists of the first thousand items to go up to auction is generated randomly, but the list of those artists is given to each player's program at the beginning of the auction.

In round j, item j in the list goes up for auction. Bids are whole numbers. The winner of the round is the player with the highest bid (provided that player has sufficent funds, otherwise the player's bid is transformed to 0). If several players all make the highest bid (perhaps after transformation), then the winner of the round is the first of those players to enter the bid. The winner of a round pays the amount of his bid. (Real estate auctions happen that way). All players are told who won the bid and what that player paid. The amount paid is subtracted from the number of units left for that player.

Here is an example. Suppose there are two players (p = 2), four artists (k = 4), and the number of items that must be obtained is 3 (n = 3). Suppose that the first several items are: t2 t3 t4 t4 t4 t2 t3 t4 t2 t4 t2 t2 t2 t3 t4.

Consider the following history: 
- player 1 wins t2 with 22 
- player 1 wins t3 with 15 
- player 0 wins t4 with 33 
- player 0 wins t4 with 33

- player 1 wins t4 with 34 
- player 1 wins t2 with 22 
- player 1 wins t3 with 0 
- player 0 wins t4 with 8 and wins the game

Architect must build a server that can accept p, k, and n as parameters. Server program will generate the order of artists or accept that order from an external source. Server should also display at every round who wins and what they paid. The server must also provide that information to the client. Finally, the server keeps track of the time spent by each client between the time the client is told of the result of the last round and the time when the client puts in the next bid. Note that this is not the same as the elapsed running time of the client.

## How to run?

The game can be downloaded from [this repo](https://github.com/samcmho/HPS-AuctionGame).
Instructions to run the game are given inside the game.

The copy of the game is available [here](AuctionGame.zip)

## Bot

Both bots are quite similar and simple work by finding the best possible artist to bid on
based on enough number of paintings available and available as soon as possible. Then the
money is divided in a quadratic manner among the bids as we want higher bids at the start and
at the end (if someone is trying to not let us win when we are close to winning) and middle bids can
be smaller as we assumed no one would care to stop us unless we are close to winning. 
Other than that, if any player is very close to winning, we try to outbid him on his preferred 
artist.