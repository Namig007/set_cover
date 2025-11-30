# SAT Project – Set Cover

This project is my solution for the SAT assignment about the Set Cover problem. Our goal in this task  is to take a Set Cover instance, encode it into SAT, solve it with Glucose 4.2, and then print which sets form the cover.

## Problem description

In this project I work with the Set Cover problem. The input describes a universe of n elements which is numbered from 1 to n, a collection of m sets, and a number k which shows at most how many sets we can take . Finally, the task is to check if these sets can together cover all elements.

Our input format for the instances is:

first line: n
second line: m
third line: k
then m lines, each describing one set: size of the set followed by the elements in that set.


An example of a valid input format is:
5

3

2

3 1 2 3

2 2 5

2 3 4

where n=5 show our elements (1,2,3,4,5), m=3 number of sets and k=2 the maximum number of sets that we can use (2 sets). The sets are S1 = {1,2,3}, S2 = {2,5}, S3 = {3,4}

A valid cover here would be S1 and S2, since together they cover all elements.

## SAT encoding

I used one boolean variable for every set, so x_j means “I take set j”. Then I added clauses so that every element must appear in at least one of the chosen sets. For each element u I simply collected all sets that contain u and put them together into one clause.

I also needed to make sure I don’t take more than k sets. I did this by adding a small counter-like construction that keeps track of how many x_j are true. This produces some extra variables, but the CNF is still straightforward.

When all clauses are ready I write them into a .cnf file in the DIMACS format. Then I call the Glucose solver on it and read its output. If the result is SAT, I look at which x_j are true and I print those sets. I also check which elements get covered in the end.

## User documentation 
 
Basic usage:

python3 Setcover.py -i instances/small.in -o formula.cnf -s glucose-syrup -v 1

Where: 
`-i` selects the instance file,
`-o` is where the CNF is written, 
`-s` is the solver executable, 
`-v` controls verbosity (0 or 1).

## Example instances


**small.in** :Very small SAT example that can be solved easily.

**unsat_missing.in**:One element never appears in any set, so we get UNSAT.  

**medium.in**: A bit bigger SAT example. 

**hard_sat.in** : This was my attempt at a larger satisfiable instance that maybe runs longer. I made blocks of 5 consecutive elements and then several overlapping sets that repeat every +5. I hoped the overlaps might slow the solver down a bit. On my laptop Glucose still solved it fast , so I did not reach 10 seconds, but this is the instance I tried as requested.


## Experiments

**small.in** → SAT. Glucose immediately found a cover.
**unsat_missing.in** → UNSAT, because one element has no set containing it.
**medium.in** → SAT. Solved quickly.
**hard_sat.in** → SAT. I wanted it to run longer but it still finished fast.

All results are matched 

