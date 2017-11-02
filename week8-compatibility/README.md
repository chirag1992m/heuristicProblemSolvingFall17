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