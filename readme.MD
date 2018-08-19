# Design

Backend generates random grids, stores solutions for a given grid.

Frontend keeps track of game state, can implement 2 type of interactions:

## Touch based interaction
User can drag finger/mouse to choose a sequence of letters, and client will query backend once the user releases his hold.

Backend will have 1 API that can be used to query for a word, and returns the validity of that word + the full amount of solutions.

## Typing based interaction
User types a words as he goes, cells on the grid will be highlighted, and client will query backend based on an "autocomplete" API that will check if the typed words are not a dead end. frontend can handle both the validness of the sequence (is it a valid path on the grid) and the validness of the words (can the typed sequence of words lead to actual word)

Backend will have 1 API that can be used to query for all the words and valid sequences on the board that can form that word.

## Problems

1) Randomizing a grid can result in a grid with no solutions. Need to skew the letter generation towards vowels

2) Solving a boggle board can be slow. Current approach is using DFS to generate all permutations of valid sequences on the grid while using a trie to terminate useless searches. One way to mitigate this is to return the randomized grid and a hash of the grid to the frontend straightaway, then the frontend can use the grid to query the backend for the solutions later on

## Developer notes:

Cells are arranged like so on the grid:

```
A1 A2 A3 A4
B1 B2 B3 B4
C1 C2 C3 C4
D1 D2 D3 D4
```
