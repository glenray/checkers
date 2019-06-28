Checkers 
Glen Pritchard - July 11, 2018

A project to learn python.

- board.py generates a list of all legal moves, including jumps (uses a nested 8x8 array to represent all squares on the board)
- board2.py uses a padded array to represent the board as described at https://www.3dkingdoms.com/checkers/bitboards.htm
- The engines folder contains player classes that use various strategies to select from the move list
- GYI.py displays the board to the user using tkinter