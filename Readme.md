Checkers 
Glen Pritchard - Aug 10, 2022
Coming back this project to implement a minimax search tree for finding the best moves. Based on the AI Algorithms for Gaming class at https://www.linkedin.com/learning/ai-algorithms-for-gaming/

- Learned how to traverse and instantiate classes programatically. See the tourn module getEngine, getEngineNames, and getUserInput methods in commit 05db2 ("git checkout 05db2") for details.


Glen Pritchard - July 11, 2018

A project to learn python.

- board.py generates a list of all legal moves, including jumps (uses a nested 8x8 array to represent all squares on the board)
- board2.py uses a padded array to represent the board as described at https://www.3dkingdoms.com/checkers/bitboards.htm
- The engines folder contains player classes that use various strategies to select from the move list
- GYI.py displays the board to the user using tkinter