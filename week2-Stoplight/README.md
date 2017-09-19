# Stoplight Shortest Path Problem

## Description
You are given a graph with costs on edges representing the time to traverse them in seconds. However, each edge also has associated with it one of k colors and edges of a each color c have two associated numbers in units of seconds greentime_c and redtime_c. Starting at time 0, the edge is passable during the first greentime_c seconds, then unpassable during the next redtime_c seconds, then passable for the next greentime_c seconds, then unpassable during the next redtime_c seconds, etc. If the edge has say 10 seconds remaining of its passable time and the time to traverse is 12 seconds, you may not traverse it nor stay in the middle (think of this as a traffic intersection). So if you start to traverse an edge, you must start in a green period and finish the traversal still in a green period with a green period throughout.

There will be approximately 200 nodes and 10000 edges and at most 10 colors. All edges are bi-directional.

The data will come in two tables. 
node1 node2 color traversetime 
color greentime redtime

Both will be in a single file. [Here is a typical file](sample_graph_file.txt).

You want to find the shortest time between source and destination where those are given as command line parameters, e.g. myfavoriteprogramminglanguage dennisprog n13 n231

Your output should simply give a sequence of edges taken and when the edge traversal begins and ends. So everyone will be given the same graph and the same starting and ending nodes. The winner(s) will find a shortest path taking into account redtimes and greentimes and of course traverse times.

## How to run the Game

## Approach to play (Bot Description)