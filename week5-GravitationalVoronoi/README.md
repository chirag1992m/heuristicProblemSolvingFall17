# Gravitational Voronoi

## Game Description
The game is played on a 1000 by 1000 grid. Given a set of 
point-sized stones (which we will call ``stones'' for simplicity) 
of various colors, a gravitational Voronoi diagram is a 
tesselation of a plane into colored regions such that every 
point x has the color of the stones that give it the greatest 
pull. The pull for a color c at point x is calculated as 
follows: Take all the stones for color c and compute the Euclidean 
distances to x, say d1, d2, ... dk. Then pull(c,x) = (1/(d1*d1)) + (1/(d2*d2)) + ... + (1/(dk*dk)). 
It's as if we're computing the color of a point based on the color 
that gives the greatest pull (in the sense of a spider web).

The Graviational Voronoi game is a two person game that works as 
follows: you and I each start with N stones (should be a command 
line parameter throughout -- no magic numbers in your programs please). 
Yours are red and mine are blue. The first player places one stone, 
then the second player places one stone and play alternates with 
each player placing one stone until the second player places 
the last stone. All stones are placed at integer locations on 
the 1000 by 1000 grid and every stone must be a Euclidean 
distance of at least 66 away from any other stone.

As the game proceeds, the Gravitational Voronoi diagram is 
computed. The display should make the stones darker than 
the other points in the region.

It may help you to see [this](https://interstices.info/jcms/c_24839/jouez-avec-les-diagrammes-de-voronoi) 
by looking at a French implementation of the non-gravitational version 
of the game

Your job is to find a strategy to play this game competitively 
on a one against one basis and as a melee in which several 
players compete.

For the two player game, we will take the sum of your scores 
as first player and second player.

## How to run the game?
Game can be downloaded from [here](https://github.com/guyu96/Gravitational_Voronoi).

A copy of the game has been provided [here](Gravitational_Voronoi.zip).

## Strategies

### [Random Bot](bot/client.py)
It simply finds a `random` valid move and makes that.

### [Cluster Bot](bot/cluster_bot.py)
Find the most optimal points to put on the grid by K-Means clustering.
If we find the optimal centroids of the grid, these centroid create
the maximum pull. To win over such a board, the opponent needs to at 
least have 2 or more stones in every cluster to win over the board.
But, a situation can easily arise where the centroid is already been 
occupied by the opponent, in that case we find the random 
nearest to centroid valid point.

To get the centroids, we run pre-computations.

## [Competitions](bot/competition.py)
Runs multiple games between any two given types of bot and present
statistics which of the bot won.