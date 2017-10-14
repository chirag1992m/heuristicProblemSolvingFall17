# Expanding Nim

## Description of the game

You and your opponent are presented with some number of stones that I will announce the day of the competition. The winner removes the last stone(s). The first player can take up to three (1, 2, or 3). At any later point in play, a player may take up to the maximum of 3 and of one more than what any previous player took, call that the currentmax.

To see how this changes the strategy from normal nim, suppose there are 8 stones to begin with. In normal Nim, the second player can force a win. Suppose the first player removes 1, 2, or 3 stones. The second player removes 3, 2, or 1 respectively, leaving the first player with four stones. If the first player removes 1, 2, or 3 stones at this point, the second player can remove the rest. However, in expanding nim, if the first player removes one stone and the second player removes three, the first player can win by removing all four that remain.

Here is another example just to show you the mechanics: if the first player removes 3, the second player can remove up to 4, in which case the first player can remove any number of stones up to and including 5.

In our tornament, two teams will play expanding nim with a reset option against each other. I will provide the initial set of stones (under 1,000). Each team will play once as the first player and once as the second player. The team may use the reset option at most four times in each game. The reset option permits a team after making its move to force the maximum number of stones that can be removed in the next turn for the other team (and in the next turn only) to be three again. After that turn play continues using the currentmax until and if some team exercises its reset option.

## Link to Game Server/Client

The game can be found at: [Munir Manan Contractor's Gitlab repository](https://gitlab.com/mmc691/expanding-nim-platform)

A copy of the game is also provided [here](expanding-nim-platform-master-74d0cde4e7529abf9beafaed5e77a226c9967873.zip).

To run the game, download the game as a compressed file and uncompress it. 

## Approach to play (Bot Description)
It was a simple game with limited and countable number of states 
to take care of with full information.

The states can be calculated by determining all the possible values used to
describe one state:

Number of players * (Number of resets^(Number of players)) * Number of 
stones left * Number of stones which can be picked up = 2 * (4**2) * 1000 * 50 = 6.4 million

These number of states can easily be pre calculated and stored in a table
by building it up using dynamic programming. Thus, one can always make the
most optimal move at any given point of time with the given set of limits
on the game states.