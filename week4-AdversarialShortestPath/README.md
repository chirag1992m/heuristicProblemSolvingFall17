# Adversarial Shortest Path Game
A route planner P is to plan a route from some source X to destination Y 
through a graph (max size of 1000 nodes) whose bi-directional edges 
have costs. Each time P traverses an edge, P's adversary A knows where 
P is and can increase the cost of any edge e by a multiplicative factor 
of 1+sqrt(k) where k is the minimum length of the shortest path from 
either node in e to Y. (Length just means number of edges.) This is a 
new rule for 2017. Adversary A can affect the same edge e more than 
once over several turns, each time by this factor 1 + sqrt(k). P is 
informed of all changes so has a chance to change the path.

Note however that if P takes the initial graph and takes the shortest 
path and that path has a single edge anywhere, then A might be able 
to make that path very expensive.

Both A and P will be told the layout of the graph (which will be fixed 
for the entire night of the contest) and the source and destination nodes.

# How to run the game?
The game can be downloaded from [here](https://github.com/chirag1992m/AdversarialShortestPathGame).

Also a copy of the game has been copied [here](AdversarialShortestPathGame.zip).

#Bot Strategy
This time we were the Architecture team and didn't participate in the game.

But here are some strategies by other teams:
- Dijkstra's algorithm simply for the player after every move. This 
didn't work at all as one may just go in circles without ever reaching it's
destination
- Some people used minimax to find the best move to make which was compute
intensive but the tree can be minimized using alpha-beta pruning and only
going to depths which are possible.
- Adversary chose to find the min-cut of the graph and increase weights in
an round-robin fashion of the edges as part of the min-cut.