# Compatibility

## Description

This is a two person game involving a Poser and a Solver. Each team will 
take on both roles, taking turns. you will be given three numbers: numpackages, 
numversions, and numcompatibles. 
Maximum values will be 20, 40, and 10000.

The Poser sets up `numpackages` packages p1, ..., `pnumpackages`. 
Each package pi has `numversions` versions: pi.v1, pi.v2, ... p.`vnumversions`. 
Poser then sets up up to `numcompatibiles` compatibility relationships. 
A compatibility relationship is of the form {p1.v5, p2.v7} which 
means that those version v5 of p1 can be in a configuration with v7 of p2.

A configuration p1.vi1, p2.vi2, p3.vi3, ... , `pnumpackages.vinumpackages` is 
acceptable if for every pair of packages pj and pk {pj.vij, pk.vik} is a 
compatibility relationship.

Configurations are governed by the following partial order: 
configuration c1 = p1.vi1, p2.vi2, p3.vi3, ... , `pnumpackages.vinumpackages` 
is greater than c2 = p1.vi1', p2.vi2', p3.vi3', ... , `pnumpackages.vinumpackages'`
if for *every j* **vij ≥ vij'** and for at least *one k* **vik > vik'**. 
A configuration c is maximal with respect to a set of configurations D, 
if no configuration c' in D has the property c' > c.

Solver's job is to find at least one maximal acceptable configuration 
and no non-maximal ones.

Play proceeds as follows: Poser ceates the compatibility relationships 
and then lists one or more acceptable configurations all within two minutes. 
That set is denoted Cposer. Architect verifies that the configurations in 
Cposer are all acceptable. If not, the Poser loses. Solver finds one or 
more acceptable configurations, denoted Csolver. Architect verifies 
that these configurations are all acceptable. If not or if Solver took 
more than two minutes, the Solver loses. Now, the Architect acts as follows: 
if for every configuration c in Csolver and every configuration c' in 
Cposer, either c and c' are incomparable or c ≥ c', then Solver wins 
else Poser wins.

Architect builds a server that takes the parameters numpackages, 
numversions, and numcompatibles. It sends this information to Poser. 
Architect then waits up to two minutes to receive Poser's set of 
compatibilites and set of supposedly acceptable configurations 
Cposer and confirms them. Then Architect sends the set of compatibilities 
to Solver and then waits up to two minutes to receive Csolver. Next, 
Architect checks who wins based on the above rules.

## How to run?
The game can be downloaded from [this repository](https://github.com/liyouvane/HPS-CG). The instructions to run are in the repo.

A copy of the game is available [here](compatibility.zip).

## Bot

### Pre-Processing
In all the bots, we do some pre processing given a problem to satisfy. The pre processing is simple
and consists of the following steps:
- Remove all those vertices which have degrees less than the number of packages-1
- We also removed edges which have "fake degrees". Every vertice should be connected to every
other package vertices. If it has multiple edges in the same package, then it is counted as one 
and the degree is counted again. If the degree is smaller than packages-1, then it is removed.

### Poser
For poser, we try to make the searching problem harder by making a clique in the middle of the
graph and adding random cliques below the graph and incomplete cliques above the graph.

### [Clique Bot](./bot/clique_bot.py)
The problem can be structured as a finding a clique in a graph with the maximum version numbers of
each package. This bot simply creates a graph of the problem, and tries to run through every possible
path from package-1 to package-n and checking if it is a clique. If it's a clique, it is added
to the list of possible solutions. When the timer ends, it simply returns the best of the possible
solutions found. This was really slow to work.

### [Satisfiability - Bot](./bot/sat_bot.py)
The problem is framed into a set of constraints and then every constraint is converted into 
a boolean expression and fed into a sat-solver to find the possible solutions. Then the best of
all the possible solutions is returned. The constraints are:
- If a px.vx, py.vy is selected, there should be an edge between them.
- There should be only one version selected for every package.
- There should be one version for every package