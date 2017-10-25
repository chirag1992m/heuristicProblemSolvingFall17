# Dancing Without Stars

## Description

This is a two player game in which there is a Choreographer and a Spoiler. Both players are presented with a board of size n by n, a number k less than n, a number of colors c, and starting positions of k dancers of each of c colors. The goal for the Choreographer is to ensure that there are disjoint, contiguous vertical or horizontal line segments of dancers, each of length c having one dancer of each color. (If c were two, this would be a a bipartite match.) In each time unit, each dancer can move either one unit row-wise or one unit column-wise. Two dancers can even swap squares. However, no two dancers can occupy the same square at the end of a time unit.

The Choreographer wants to use as few time units (parallel steps) as possible to get to a paired-up state. The Spoiler wants to make the Choreographer use more time Players will play both as Spoiler and as Choreographer.

The Spoiler may place stars on k squares on the board on empty squares before the dancers have begun to move. No two stars may be closer than c+1 apart (Manhattan distance). The Choreographer is told where those stars are. The Choreographer is not allowed to use those squares.

Example: set-up where c is 4 and there are 40 dancers of each color. Here is a [typical format](dancedata.txt).

## How to run the game?

The game can be downloaded from architects [repo](https://bitbucket.org/taikun/dancing-without-stars).

A copy of the game has been provided [here](dancing-without-stars.zip).

The instructions to run are given in README.md of the game directory.

## Bots