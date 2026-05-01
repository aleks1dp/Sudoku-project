SET08122 Algorithms & Data Structures Coursework
Command-Line Sudoku Game 

Files Included:
sudoku_main.py
README.txt
sudoku_history.json (generated  when the game is played)

Requirements:
1. Make sure the latest version of Python is installed by running: 
    python --version
in terminal. At the time of the creation of the game, the version used was Python 3.11.5.
2. Navigate to the folder containing sudoku_main.py: 
    cd path/to/your/folder
3. Run the game:
    python sudoku_main.py
4. The main menu will appear. Use your keyboard as instructed to navigate.
4. The main menu will appear. Use your keyboard to navigate. Note that the the game is terminal/command-line only, 
but also uses ANSI escape codes for color coding, which is supported by most terminals, so try a different terminal if the visuals are off.

NOTE: The below features will also be displayed during gameplay, so beyond this point the instructions that are provided when 
running the game should be sufficient.

Game Features:
1.  Easy, Medium, and Hard difficulty levels
  a. Timed mode
2.  Undo and Redo functionality
3.  Hint system (first hint free)
  a. Mini 4×4 Sudoku challenge to unlock extra hints
4.  Move history saving
  a. Replay previous games (auto-playback)
  b. Replay same starting board as a new game
  c. Resume incomplete games
5. Mistake counter (max 3 before game over)
6. Digit placement tracker
7. Color-coded terminal interface

Game Rules: 
- Fill the 9x9 grid so that every row, column, and 3x3 box contains the digits 1 to 9 once.
  Specific to this gameply:
  - White numbers are fixed clues and cannot be changed.
  - Blue numbers are your valid placements.
  - Red numbers indicate an incorrect placement.
  - You are allowed a maximum of 3 mistakes before the game ends.

Controls During Gameplay:
- row col num: Place a number (eg "3 5 7" places 7 at row 3, col 5)
- row col 0: Clear a cell (eg "3 5 0")
- u: Undo the last move
- r: Redo a previously undone move
- h: Request a hint (first hint is free but after that you must solve a mini 4x4 Sudoku puzzle to earn it)
- q: Quit and save the current game to history

Save and Replay Functionality: 
- Games are automatically saved when you press q or when the game end due to a win, a loss, or atimeout. Save data is stored in 
sudoku_history.json in the same folder as sudoku_main.py.
- From the Replay menu you can either:
  a.  Watch a playback of a past game
  b.  Replay the same starting board from scratch as a new game

Resetting Saved Data: 
If you encounter errors loading saved games, you may need to delete the save file so it can be regenerated. Delete sudoku_history.json from the same folder as sudoku.py:
  Mac/Linux:
    rm "/path/to/your/folder/sudoku_history.json"
  Windows:
    del "C:\path\to\your\folder\sudoku_history.json"

Or find and delete sudoku_history.json manually in your system's file manager.
The file will be recreated automatically the next time you finish or quit a game. However, note that all of your previous games will be deleted