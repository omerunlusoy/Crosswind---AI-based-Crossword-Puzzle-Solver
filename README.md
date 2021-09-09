# Crosswind---AI-based-Crossword-Puzzle-Solver

AI based NYTimes Crossword Puzzle Solver

Crossword is a type of puzzle, offering clues with word plays for humans to come up with answers that fills a grid. To have any chance of success with such a puzzle, the solver is required to have some knowledge about popular culture, history, and language (a.k.a. common sense).

In this project, the aim was to create an AI based program that solves the Newyork Times mini crossword puzzle designed by Joel Fagliano. This is a 5x5 puzzle that has 5 across and 5 down clues and their corresponding entries. The entries usually have many crossings which creates lots of constraints. This makes the puzzle more approachable to AI based programs.

Our program searches several sources on the internet to retrieve possible answers for clues and selects a set of answers from them. The online sources used were merriam-webster’s dictionary and thesaurus, and Wikipedia. We also downloaded Wordnet and used it as an offline resource. Constraint satisfaction and depth first search were used in the solution process. In the following sections, the approaches used throughout the project will be described and the results will be evaluated.

Example Run:

![alt text](https://github.com/omerunlusoy/Crosswind---AI-based-Crossword-Puzzle-Solver/blob/main/Final%20Report/example.png)
