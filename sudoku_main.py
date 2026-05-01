import random #unique numbers each game
import time #timer function of the game
import copy #creates a copy for gameplay to retain the original solution
import json #saves and loads game state
import os #checks whether a save file exists
from datetime import datetime


class Colors:
    BOLD = '\033[1m'
    DIM = '\033[2m' # for empty cells to differentiate them from filled cells
    RESET = '\033[0m' #changes back the color to original after
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'


class Board:
    size = 9 #9x9 grid
    base = 3 #3X3 boxes 

    #helper function for initialzing the grid and fixed arrays
    def createGrid(self, default = 0): 
        return [[default for  _ in range(self.size)] for _ in range(self.size)]

    def __init__(self):
        self.grid = self.createGrid(0) #empty grid of 9x9
        self.fixed = self.createGrid(False) #player is not allowed to change these cells if changed to True boolean array to track which cells are fixed
        self.solution = [] #copy of the completed grid to check against player's input

    def rowValid(self, row: int, num: int, col_exclude: int = -1) -> bool:
        for c in range(self.size):
            if c == col_exclude:
                continue #skip this cell 
            if self.grid[row][c] == num: #if the number is found in the same row, it's not valid
                return False
        return True #otherwise it's valid
    
    def colValid(self, col: int, num: int, row_exclude: int = -1) -> bool:
        for r in range(self.size):
            if r == row_exclude:
                continue
            if self.grid[r][col] == num: #if the number is found in the same column, it's not valid
                return False
        return True #otherwise it's valid
    
    def boxValid(self, row: int, col: int, num: int, rowExclude: int = -1, colExclude: int = -1) -> bool:
        box_row_start = (row // self.base) * self.base # starting point. example: row 5 so 5/3=1 
                                                        # then 1*3 = 3 so the top of the 3x3 box is 3
        box_col_start = (col // self.base) * self.base
        for r in range(box_row_start, box_row_start + self.base):
            for c in range(box_col_start, box_col_start + self.base):
                if (r, c) != (rowExclude, colExclude): # skip the cell we are placing into -- doesn't conflict with itself
                    if self.grid[r][c] == num: #if the number is found in the same 3x3 box, it's not valid
                        return False
        return True #otherwise it's valid
    
    def isValid(self, row: int, col: int, num: int) -> bool: # checks for all three conditions for a valid placement
        return self.rowValid(row, num, col) and self.colValid(col, num, row) and self.boxValid(row, col, num, row, col)
    
    def is_cell_fixed(self, row: int, col: int) -> bool:
        return self.fixed[row][col] #has a value that player cannot change
    
    def setCell(self, row: int, col: int, num: int, fixed: bool = False):
        self.grid[row][col] = num #sets the value of the cell to the number provided
        self.fixed[row][col] = fixed #if fixed is True, player cannot change this cell

    def getCell(self, row: int, col: int) -> int:
        return self.grid[row][col] #returns the value of the cell

    def complete(self):
        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row][col] == 0: #if any cell is empty, the board is not complete
                    return False
                if self.solution and self.grid[row][col] != self.solution[row][col]: #checks whether filled incorrectly
                    return False
        return True #otherwise it's complete
    
    def remainingCells(self) -> dict:
        placed = {n: 0 for n in range(1, self.size + 1)} #dictionary to count how many of each number has been placed
        for row in range(self.size): # counts how many times a number is on the 9x9 grid and updates the dictionary accordingly
            for col in range(self.size):
                if self.grid[row][col] != 0:
                    placed[self.grid[row][col]] += 1
        return placed
    
    def copyGrid(self):
        return copy.deepcopy(self.grid) #creates a  copy of the grid to retain the original solution for checking against player's input
    

class SudokuGenerator:
    CLUES = {"easy": 40, "medium": 32, "hard": 25}  #number of clues for each difficulty level

    def generate(self, difficulty: str):
        self.board = Board() #creates a blank board
        self.fill(self.board.grid) #fill the board with solution
        self.board.solution = self.board.copyGrid() #saves the completed grid as the solution before removign cells depending on the difficulty level
        self.removeCells(self.board, difficulty) #removes cells based on the difficulty chosen

        for row in range(self.board.size):
            for col in range(self.board.size): 
                self.board.fixed[row][col] = (self.board.grid[row][col] != 0) #every cell that is not empty is marked as fixed so the player cannot change it
        return self.board 
    
    def fill(self, grid: list):
        for row in range(Board.size):
            for col in range(Board.size):
                if grid[row][col] == 0: #finds the first empty cell
                    numbers = list(range(1, Board.size + 1)) #1-9 numbers to try placing in the cell
                    random.shuffle(numbers) #randomize the 1-9 numbers
                    for num in numbers:
                        if self.isValid(grid, row, col, num): #checks if placing the number is valid 
                            grid[row][col] = num #places the number in the cell
                            if self.fill(grid): #recur until the board is completely filled
                                return True
                            grid[row][col] = 0 #backtracks if it leads to an invalid state
                    return False #if no number can be placed, backtrack
        return True #if the grid is completely filled, return True

    @staticmethod #helps with organizaition since this function is only used for generating the board and doesn't rely on any instance variables
    def isValid(grid: list, row: int, col: int, num: int):
        if num in grid[row]: #check row first
            return False
        if any(grid[r][col] == num for r in range(Board.size)): #check column -- look at the same column in every row to see if the number is present
            return False
        box_row_start = (row // Board.base) * Board.base # 0 3 or 6
        box_col_start = (col // Board.base) * Board.base
        for r in range(box_row_start, box_row_start + Board.base):
            for c in range(box_col_start, box_col_start + Board.base):
                if grid[r][c] == num: 
                    return False # checks and returns false if the number is found in the same box
        return True # if num is not found in the row, column, or box, it's valid to place it there
    
    def removeCells(self, board, difficulty: str):
        clues = self.CLUES.get(difficulty, 32) #default to medium if invalid difficulty is provided
        cells_to_remove = Board.size * Board.size - clues #remove based on difficulty
        cells = [(r, c) for r in range(Board.size) for c in range(Board.size)] #list of all cell coordinates
        random.shuffle(cells) #randomize the order of the cells to remove
        removed = 0
    
        for row, col in cells:
            if removed >= cells_to_remove: #no need to continue if we've removed enough cells
                break
            fail_safe = board.grid[row][col] #store the original value of the cell to restore it if removing it leads to multiple solutions
            board.grid[row][col] = 0 #clear the cell to create a clue

            test_grid = copy.deepcopy(board.grid) #create a copy of the board to test if it still has a solution after removing the cell
            count = [0]
            self.countSolutions(test_grid, count) #count the number of solutions for the test board
            count = count[0]
            if count != 1: #if the test board does not have a unique solution
                board.grid[row][col] = fail_safe #restore the original value
            else:
                removed += 1 #keep the removal as the sol is unique and increment the count of removed cells

    def countSolutions(self, grid, count, limit=2): #2 or more solutions = not unique
        if count[0] >= limit:
            return

        for row in range(Board.size):
            for col in range(Board.size):
                if grid[row][col] == 0: #empty cell
                    for num in range(1, Board.size + 1): # go from 1-9 to try placing in the empty cell
                        if self.isValid(grid, row, col, num): #check if placing the number is valid
                            grid[row][col] = num 
                            self.countSolutions(grid, count, limit) #recur to count solutions for the remaining cells
                            grid[row][col] = 0 #backtrack
                            if count[0] >= limit: #no empty cells found, stop searching
                                return
                    return #return the number of solutions found so far
        count[0] += 1
                
# board for the mini game -- practically same code as the main board but with a 4x4 grid and 2x2 boxes 
class MiniBoard:
    size = 4
    base = 2

    def createGrid(self, default = 0): 
        return [[default for i in range(self.size)] for i in range(self.size)]

    def __init__(self):
        self.grid = self.createGrid(0)
        self.fixed = self.createGrid(False)
        self.solution = []

    def rowValid(self, row: int, num: int, col_exclude: int = -1) -> bool:
        for c in range(self.size):
            if c == col_exclude:
                continue
            if self.grid[row][c] == num:
                return False
        return True
    
    def colValid(self, col: int, num: int, row_exclude: int = -1) -> bool:
        for r in range(self.size):
            if r == row_exclude:
                continue
            if self.grid[r][col] == num:
                return False
        return True
    
    def boxValid(self, row: int, col: int, num: int, row_exclude: int = -1, col_exclude: int = -1) -> bool:
        box_row_start = (row // self.base) * self.base
        box_col_start = (col // self.base) * self.base
        for r in range(box_row_start, box_row_start + self.base):
            for c in range(box_col_start, box_col_start + self.base):
                if (r, c) != (row_exclude, col_exclude):
                    if self.grid[r][c] == num:
                        return False
        return True
    
    def isValid(self, row: int, col: int, num: int) -> bool:
        return self.rowValid(row, num, col) and self.colValid(col, num, row) and self.boxValid(row, col, num, row, col)
    
    def is_cell_fixed(self, row: int, col: int) -> bool:
        return self.fixed[row][col]
    
    def setCell(self, row: int, col: int, num: int, fixed: bool = False):
        self.grid[row][col] = num
        self.fixed[row][col] = fixed

    def getCell(self, row: int, col: int) -> int:
        return self.grid[row][col]

    def complete(self) -> bool:
        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row][col] == 0:
                    return False
                if self.solution and self.grid[row][col] != self.solution[row][col]:
                    return False
        return True
    
    def remainingCells(self) -> dict:
        placed = {n: 0 for n in range(1, self.size + 1)}
        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row][col] != 0:
                    placed[self.grid[row][col]] += 1
        return placed
    
    def copyGrid(self):
        return copy.deepcopy(self.grid)
    
class MiniSudokuGenerator:
    CLUES = 6  # always 6 revealed cells, no matter the difficulty of the main board, for simplicity

    def generate(self): # same code as with the main board 
        self.board = MiniBoard()
        self.fill(self.board.grid)
        self.board.solution = self.board.copyGrid()
        self.removeCells(self.board)

        for row in range(self.board.size):
            for col in range(self.board.size):
                self.board.fixed[row][col] = (self.board.grid[row][col] != 0)
        return self.board
    
    def fill(self, grid: list): #same code as for the main board
        for row in range(MiniBoard.size):
            for col in range(MiniBoard.size):
                if grid[row][col] == 0:
                    numbers = list(range(1, MiniBoard.size + 1))
                    random.shuffle(numbers)
                    for num in numbers:
                        if self.isValid(grid, row, col, num):
                            grid[row][col] = num
                            if self.fill(grid):
                                return True
                            grid[row][col] = 0
                    return False
        return True

    @staticmethod #same code as for the main board
    def isValid(grid: list, row: int, col: int, num: int) -> bool:
        if num in grid[row]:
            return False
        if any(grid[r][col] == num for r in range(MiniBoard.size)):
            return False
        box_row_start = (row // MiniBoard.base) * MiniBoard.base
        box_col_start = (col // MiniBoard.base) * MiniBoard.base
        for r in range(box_row_start, box_row_start + MiniBoard.base):
            for c in range(box_col_start, box_col_start + MiniBoard.base):
                if grid[r][c] == num:
                    return False
        return True
    
    def removeCells(self, board):
        clues = self.CLUES
        cells_to_remove = MiniBoard.size * MiniBoard.size - clues #remove based on difficulty
        cells = [(r, c) for r in range(MiniBoard.size) for c in range(MiniBoard.size)] #list of all cell coordinates
        random.shuffle(cells) #randomize the order of the cells to remove
        removed = 0

        for row, col in cells:
            if removed >= cells_to_remove: #no need to continue if we've removed enough cells
                break
            fail_safe = board.grid[row][col] #store the original value of the cell to restore it if removing it leads to multiple solutions
            board.grid[row][col] = 0 #clear the cell to create a clue

            test_grid = copy.deepcopy(board.grid) #create a copy of the board to test if it still has a solution after removing the cell
            count = [0]
            self.countSolutions(test_grid, count) #count the number of solutions for the test board
            count = count[0]
            if count != 1: #if the test board does not have a unique solution
                board.grid[row][col] = fail_safe #restore the original value
            else:
                removed += 1 #keep the removal as the sol is unique and increment the count of removed cells

    def countSolutions(self, grid, count, limit=2): #2 or more solutions = not unique
        if count[0] >= limit:
            return

        for row in range(MiniBoard.size):
            for col in range(MiniBoard.size):
                if grid[row][col] == 0: #empty cell
                    for num in range(1, MiniBoard.size + 1): # go from 1-4 to try placing in the empty cell
                        if self.isValid(grid, row, col, num): #check if placing the number is valid
                            grid[row][col] = num
                            self.countSolutions(grid, count, limit) #recur to count solutions for the remaining cells
                            grid[row][col] = 0 #backtrack
                            if count[0] >= limit: #stop early if we've found enough solutions
                                return
                    return #return the number of solutions found so far
        count[0] += 1


class GameState:
    __slots__ = ("row", "col", "old_num", "new_num", "timestamp") #only allows these attributes for each GameState instance

    def __init__(self, row: int, col: int, old_num: int, new_num: int):
        self.row = row
        self.col = col
        self.old_num = old_num # before move (undo functionality)
        self.new_num = new_num # after move (redo/replay fucntionality)
        self.timestamp = time.time() #when this happened during gameplay

    def toDict(self)-> dict: #converts to dict for json serialization when saving the game state to a file
        return {
            "row": self.row,
            "col": self.col,
            "old_num": self.old_num,
            "new_num": self.new_num,
            "timestamp": self.timestamp
        }
    
class UndoRedo:
    def __init__(self):
        self.undo_stack  = []
        self.redo_stack = []

    def push(self, state: GameState):
        self.undo_stack.append(state) #add the new game state to the undo stack
        self.redo_stack.clear() #clear the redo stack since we can only redo immediately after an undo
    
    def undo(self) -> GameState:
        if not self.undo_stack:
            return None 
        state = self.undo_stack.pop() #most recent game state from the undo stack
        self.redo_stack.append(state) #add it to the redo stack 
        return state 
    
    def redo(self):
        if not self.redo_stack:
            return None 
        state = self.redo_stack.pop() #most recent game state from the redo stack
        self.undo_stack.append(state) #add it back to the undo stack since we are redoing it
        return state
    
    def canUndo(self): 
        return bool(self.undo_stack) #1+ move that can be undone
    
    def canRedo(self):
        return bool(self.redo_stack) #1+ move that can be redone
    
    def history(self) -> list:
        return self.undo_stack + self.redo_stack[::-1] #combine undo and redo stacks to show full history of moves, with undo moves in order and redo moves in reverse order since they are undone moves
    
    def clear(self): #cleared at the stat of a new game to reset the move history
        self.undo_stack.clear() 
        self.redo_stack.clear()

    
HISTORY_FILE = "sudoku_history.json" #file to save the move history for replay and viewing of past games 
                                    #containing information such as the difficulty, whether the game was completed, elapsed time, and the sequence of moves made by the player for replaying later

class SudokuGameHistory:
    def __init__(self):
        self.sessions: list = self.load() # load previously saved sessions

    def load(self) -> list:
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r") as f:
                    return json.load(f) #load the history from the file
            except (json.JSONDecodeError, IOError):
                return [] #if the file is corrupted or cannot be read, return empty list
        return [] #no history file found, return empty list
    
    def save(self, session: dict):
        self.sessions.append(session) #add the new session to the list of sessions
        try:
            with open(HISTORY_FILE, "w") as f:
                json.dump(self.sessions, f, indent=4) #save the updated sessions list to the file 
        except (json.JSONDecodeError, IOError):
            pass #if the file cannot be written to, ignore the error
    
    def listSessions(self)->list:
        return self.sessions #return the list of saved sessions for replaying past games
    
    def getSession(self, index: int) -> dict:
        if 0 <= index < len(self.sessions):
            return self.sessions[index] #return the session at the specified index if it exists
        return None #invalid index (out of bound) return None
    

class Display:
    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear') #clear between moves for better readability

    @staticmethod
    def title():
        print(f"""{Colors.BOLD}{Colors.BLUE}Welcome to Sudoku!{Colors.RESET}\n""") 
    
    @staticmethod
    def board(board, highlight=None, mistakes = None, elapsed = None, time_limit = None):

        #timer on top right of the board
        if elapsed is not None:
            mins = int(elapsed) // 60
            secs = int(elapsed) % 60
            timer = f"Timer: {int(mins):02d}:{int(secs):02d}"

            if time_limit is not None: #if in timed mode, also show the remaining time
                remaining_time = max(0, int(time_limit) - int(elapsed))
                mins_remain = remaining_time // 60
                secs_remain = remaining_time % 60
                timer += f" | Remaining: {int(mins_remain):02d}:{int(secs_remain):02d}"
            print(f"{Colors.BOLD}{Colors.YELLOW}{timer}{Colors.RESET}\n")

        size = board.size #get the size of the board

        #column headers
        print(f"\n{Colors.DIM}     1  2  3 | 4  5  6 | 7  8  9{Colors.RESET}")
        print(f"{Colors.DIM}   ───────────────────────────────{Colors.RESET}")

        #rows of the board
        for row in range(size):
            if row > 0 and row % board.base == 0:
                print(f"{Colors.DIM}   ───────────────────────────────{Colors.RESET}")
            row_str = f"{Colors.DIM} {row + 1} │{Colors.RESET}"
            for col in range(size):
                cell_value = board.getCell(row, col)
                cell_str = f"{cell_value}" if cell_value != 0 else " " #empty cells are shown as blank spaces
                if highlight and (row, col) in highlight:
                    cell_color = Colors.YELLOW + Colors.BOLD #highlight hinted cells in yellow
                elif mistakes and (row, col) in mistakes:
                    cell_color = Colors.RED + Colors.BOLD #highlight incorrect cells in red
                elif board.is_cell_fixed(row, col):
                    cell_color = Colors.WHITE + Colors.BOLD #clues are highlighted in white
                elif cell_value != 0:
                    cell_color = Colors.BLUE + Colors.BOLD #correct inputs are highlighted in blue
                else:
                    cell_color = Colors.DIM #empty cells are dimmed to differentiate them from filled cells
                row_str += f" {cell_color}{cell_str}{Colors.RESET}" #color the cell value based on its status 
                if col in [2, 5]: #vertical separators for boxes
                    row_str += f" {Colors.DIM}|{Colors.RESET}"
                else:
                    row_str += " " #regular space between cells
            print(row_str)
        print(f"\n{Colors.DIM}   ───────────────────────────────{Colors.RESET}")

    @staticmethod #allows to call an instance of Display without needing to create an object since this function is only used for displaying the remaining numbers and doesn't rely on any instance variables
    def remNumbers(board: Board):
        remaining = board.remainingCells() #get the count of how many of each number has been placed on the board
        print(f"\n{Colors.MAGENTA}{Colors.BOLD}Numbers Placed:{Colors.RESET}")
        line = "" #initialise line before the loop
        for num in range(1, board.size+ 1):
            count = remaining[num] #how many have been placed
            if count == board.size:  # all 9 placed
                cell_color = Colors.GREEN + Colors.BOLD
            elif count <= 3:
                cell_color = Colors.YELLOW + Colors.BOLD #few are placed, so it's a good number to place
            else:
                cell_color = Colors.WHITE + Colors.BOLD #most are still needed to be placed
            line += f"{cell_color}{num}:{Colors.RESET} {count}  " #show the number and how many have been placed
        print(line +"\n")

    @staticmethod
    def menu():
        print(f"\n{Colors.BOLD}{Colors.CYAN}MAIN MENU {Colors.RESET}")
        print("1. How to Play")
        print("2. New Game")
        print("3. Replay Previous Game")
        print("4. View Game History")
        print("5. Quit")

    @staticmethod
    def difficulty_menu():
        print(f"\n {Colors.BOLD}{Colors.CYAN}Select Difficulty:{Colors.RESET}")
        print("a. Easy   (40 clues)")
        print("b. Medium (32 clues)")
        print("c. Hard   (25 clues)")
        print("t. Timed Mode")
        print("x. Back")

    @staticmethod
    def help_text():
        print("\n HOW TO PLAY SUDOKU\n")
        print("Fill the 9x9 grid so each row, column, and 3x3 box")
        print("contains the digits 1 to 9 exactly once.\n")
        print("Enter moves as: row col digit  (e.g., 3 5 7)")
        print("Clear a cell: row col 0")
        print("u - Undo last move")
        print("r - Redo an undone move")
        print("h - Hint")
        print("s - Show remaining numbers")
        print("q - Quit the game")
        input("\nPress 'Enter' to continue...")

# Mini game
def display_mini(board):
    print("\nSolve this mini Sudoku to earn your hint!\n")
    print(f"{Colors.DIM}     1  2 | 3  4{Colors.RESET}")
    print(f"{Colors.DIM}   ─────────────{Colors.RESET}")
    for row in range(board.size):
        if row > 0 and row % board.base == 0:
            print(f"{Colors.DIM}   ─────────────{Colors.RESET}")
        row_str = f"{Colors.DIM} {row + 1} │{Colors.RESET}"
        for col in range(board.size):
            cell_value = board.getCell(row, col)
            cell_str = f"{cell_value}" if cell_value != 0 else " " #empty cells are shown as blank spaces
            if board.is_cell_fixed(row, col):
                cell_color = Colors.WHITE + Colors.BOLD #clues are highlighted in white
            elif cell_value != 0:
                cell_color = Colors.BLUE + Colors.BOLD #correct inputs are highlighted in blue
            else:
                cell_color = Colors.DIM #empty cells are dimmed to differentiate them from filled cells
            row_str += f" {cell_color}{cell_str}{Colors.RESET}" #color the cell value based on its status 
            if col in [1]: #vertical separators for boxes
                row_str += f" {Colors.DIM}|{Colors.RESET}"
            else:
                row_str += " " #regular space between cells
        print(row_str)
    print(f"\n{Colors.DIM}   ─────────────{Colors.RESET}")

def play_mini_game():
    gen = MiniSudokuGenerator() #new generator for mini sudoku
    board = gen.generate()

    while True:
        Display.clear()
        display_mini(board)

        if board.complete():
            print("Mini Sudoku solved! Hint unlocked.\n")
            time.sleep(1) #just arbitrary add downtime for readanbility and user experience
            return True

        move = input(f"{Colors.DIM}{Colors.MAGENTA}Enter move (row col num) or q: {Colors.RESET}").strip().lower()
        if move == 'q': 
            return False #forfeit the mini game and not get the hint

        try:
            r, c, n = map(int, move.split()) #convert the input into integers for row, column, and number
            r -= 1  #adjust for 0 indexing
            c -= 1
        except:
            print("Invalid input") # cannot be converted to integers/wrong format
            continue

        if board.fixed[r][c]: #cell is fixed and cannot be changed
            print("Cannot change fixed cell")
            continue

        if board.isValid(r, c, n): #check whether valid , if not print message
            board.grid[r][c] = n
        else:
            print("Invalid move")

class SudokuGamePlay:
    def __init__(self):
        self.board = None
        self.undoRedo = UndoRedo()
        self.history = SudokuGameHistory()
        self.generator = SudokuGenerator()
        self.startTime = 0.0
        self.timeLimit = None
        self.freebieUsed = False
        self.mistakeCount = 0
        self.display = Display()

    def newGame(self, difficulty: str, time_limit: int = None):
        self.board = self.generator.generate(difficulty) #new board based on the selected difficulty
        self.undoRedo = UndoRedo()#clear the undo redo history 
        self.startTime = time.time() #start the timer
        self.timeLimit = time_limit #set the time limit
        self.freebieUsed = False
        self.mistakeCount = 0
        self.initialBoard = self.board.copyGrid()
        self.gameLoop(difficulty) #start the game loop for player input and interaction

    def gameLoop(self, difficulty: str):
        mistakes = set() #track incorrect placements to highlight them on the board
        while True:
            self.display.clear()
            self.display.title()
            elapsed = time.time() - self.startTime #calculate elapsed time
            
            difficulty_color = {
                "easy": Colors.GREEN,
                "medium": Colors.YELLOW,
                "hard": Colors.RED,
                "timed": Colors.MAGENTA
            }.get(difficulty, Colors.WHITE) 

            canUndo = self.undoRedo.canUndo()
            canRedo = self.undoRedo.canRedo()
            undoColor = Colors.GREEN if canUndo else Colors.DIM #green if undo is available, dim if not
            redoColor = Colors.GREEN if canRedo else Colors.DIM 
            undoText = "YES" if canUndo else "no"
            redoText = "YES" if canRedo else "no"

            mistakeColor = Colors.GREEN if self.mistakeCount == 0 else Colors.YELLOW if self.mistakeCount == 1 else Colors.RED #green for no mistakes, yellow for 1 mistake, red for 2 or more mistakes
            print(
                f" Difficulty: {difficulty_color}{difficulty.upper()}{Colors.RESET}  "
                f"|  Undo: {undoColor}{undoText}{Colors.RESET}  "
                f"|  Redo: {redoColor}{redoText}{Colors.RESET}  "
                f"|  Mistakes: {mistakeColor}{self.mistakeCount}/3{Colors.RESET}\n"
            )

            self.display.board(self.board, mistakes = mistakes, elapsed=elapsed, time_limit=self.timeLimit) #display the board with the timer and time limit if in timed mode
            self.display.remNumbers(self.board) #show how many of each number have been placed and how many are remaining
            
            if self.timeLimit and elapsed >= self.timeLimit: #check if time limit has been reached
                print(f"{Colors.RED}{Colors.BOLD}Time's up! Game over.{Colors.RESET}\n")
                self.saveHistory(difficulty, completed = False, elapsed=elapsed) #save the game history even if they didn't finish for replaying later
                input("Press 'Enter' to return to the main menu...")
                return #return to main menu after time's up

            if self.board.complete(): #check if the board is complete after each move
                elapsed = time.time() - self.startTime #final elapsed time
                self.display.clear()
                self.display.title()
                self.display.board(self.board)
                mins = int(elapsed) // 60
                secs = int(elapsed) % 60
                print(f"{Colors.GREEN}{Colors.BOLD}Congratulations! You solved the puzzle in {mins:02d} minutes and {secs:02d} seconds!{Colors.RESET}\n")
                self.saveHistory(difficulty, completed=True, elapsed=elapsed) #save the game history
                input("Press 'Enter' to return to the main menu...")
                return

            rawInput = input(f"{Colors.DIM}{Colors.MAGENTA}Enter your move (row col num), or 'u' undo, 'r' redo, 'h' hint, 'q' quit: {Colors.RESET}").strip().lower()

            if rawInput == 'q': #quit the game
                self.saveHistory(difficulty, completed=False, elapsed=time.time()-self.startTime) #save the game history
                print(f"{Colors.YELLOW}Game saved. Returning to main menu...{Colors.RESET}\n")
                time.sleep(1)
                return
            
            if rawInput == 'u': #undo the last move
                self.doUndo(mistakes)
                continue

            if rawInput == 'r': #redo the last undone move
                self.doRedo(mistakes)
                continue    

            if rawInput == 'h': #provide a hint by filling in one of the empty cells with the correct value from the solution
                self.hint(mistakes)
                continue

            # if rawInput == 's': #show how many of each number have been placed and how many are remaining
            #     input("Press 'Enter' to continue...")
            #     continue 

            #verifying inputs
            parts = rawInput.split()
            if len(parts) != 3: # not 3 string values separated by spaces as instructed
                print(f"{Colors.RED}Invalid input format. Please enter: row col num{Colors.RESET}")
                time.sleep(1)
                continue

            try:
                row, col, num = map(int, parts) #convert input to integers
                row -= 1  #adjust for 0 indexing
                col -= 1

            except ValueError:
                print(f"{Colors.RED}Invalid input. Row, column, and number must be integers.{Colors.RESET}")
                time.sleep(1)
                continue

            if not (0 <= row < self.board.size and 0 <= col < self.board.size): #check if row and column are within the valid range of the board
                print(f"{Colors.RED}Row and column must be between 1 and {self.board.size}.{Colors.RESET}")
                time.sleep(1)
                continue

            old = self.board.getCell(row, col) #store the old value of the cell for undo 

            if num != 0 and not self.board.isValid(row, col, num): #check if the move is valid 
                print(f"{Colors.RED}Invalid move {num} cannot be placed at ({row + 1}, {col + 1}).{Colors.RESET}")
                mistakes.add((row, col)) #add to mistakes set
                self.mistakeCount += 1 #increment the mistake count
                remaining_mistakes = 3 - self.mistakeCount # max 3 mistakes allowed before game over
                if self.mistakeCount >= 3: # if more than 3 mistakes, game over
                    self.display.clear()
                    self.display.title()
                    self.display.board(self.board, mistakes=mistakes)
                    print(f"{Colors.RED}{Colors.BOLD}3 mistakes made. Game over!{Colors.RESET}\n")
                    self.saveHistory(difficulty, completed=False, elapsed=time.time() - self.startTime) #save the game history even if they didn't finish for replaying later
                    input("Press 'Enter' to return to the main menu...")
                    return
                print(f"{Colors.RED}Invalid move! {num} cannot be placed at ({row + 1}, {col + 1}). "
                    f"Mistakes: {self.mistakeCount}/3 ({remaining_mistakes} remaining){Colors.RESET}")
                time.sleep(1)
                continue

            mistakes.discard((row, col)) #if the move is valid, remove from mistakes

            move = GameState(row, col, old, num) #create a new game state for the move
            self.undoRedo.push(move) #add the move to the undo stack
            self.board.setCell(row, col, num) #update the game board with the new move

    def doUndo(self, mistakes: set):
        move = self.undoRedo.undo() #get the most recent move from the undo stack to redo
        if not move: #nothing to undo
            print(f"{Colors.DIM}No moves to undo.{Colors.RESET}")
            time.sleep(1)
            return
        else:
            self.board.setCell(move.row, move.col, move.old_num) #revert by setting the cell back to the old value
            mistakes.discard((move.row, move.col)) #discard regardless since we are undoing
            print(f"{Colors.GREEN}Undone: cell ({move.row+1},{move.col+1}) restored to {move.old_num if move.old_num else 'empty'}{Colors.RESET}")
            time.sleep(1)

    def doRedo(self, mistakes: set):
        move = self.undoRedo.redo() #get the most recent undone move from the redo stack to undo
        if not move:
            print(f"{Colors.DIM}No moves to redo.{Colors.RESET}")
            time.sleep(1)
            return
        else:
            self.board.setCell(move.row, move.col, move.new_num) #reapply the move by setting the cell to the new value
            if move.new_num != 0 and not self.board.isValid(move.row, move.col, move.new_num): #if the move being redone is incorrect, add it back to the mistakes set
                mistakes.add((move.row, move.col))
            else:
                mistakes.discard((move.row, move.col)) #if the move being redone is correct, remove it from the mistakes set if it was there
            print(f"{Colors.GREEN}Redone: cell ({move.row+1},{move.col+1}) set to {move.new_num if move.new_num else 'empty'}{Colors.RESET}")
            time.sleep(1)

    def hint(self, mistakes: set):
        empty_cells = [(r, c) for r in range(self.board.size) for c in range(self.board.size) if self.board.getCell(r, c) == 0] #list of all empty cells
        if not empty_cells:
            print(f"{Colors.DIM}No empty cells to provide a hint for.{Colors.RESET}")
            time.sleep(1)
            return
        if self.freebieUsed: #only allow 1 hint per game
            print(f"{Colors.YELLOW}To earn a hint, solve  mini Sudoku first!{Colors.RESET}")
            time.sleep(1)
            self.display.clear()

            if not play_mini_game():
                print(f"{Colors.RED}Hint not earned. Returning to game...{Colors.RESET}")
                time.sleep(1)
                return

        row, col = random.choice(empty_cells) #randomly select an empty cell to provide a hint for
        correct_num = self.board.solution[row][col] #get the correct solution

        self.undoRedo.push(GameState(row, col, 0, correct_num)) #record the hint as a move
        self.board.setCell(row, col, correct_num) #fill in the cell with the correct number from the solution
        self.freebieUsed = True #mark that the free hint has been used
        print(f"{Colors.GREEN}Hint: cell ({row+1},{col+1}) set to {correct_num}{Colors.RESET}")
        time.sleep(1)
    

    def saveHistory(self, difficulty: str, completed: bool, elapsed: float):
        session = {
            "timestamp": datetime.now().isoformat(), #when the game was played
            "difficulty": difficulty,
            "completed": completed,
            "elapsed": round(elapsed, 2), #round to 2 decimal places for readability
            "solution": self.board.solution, #save the solution for replaying later
            "initial_board": self.initialBoard, #save the initial board state for replaying later
            "fixed_cells": [row[:] for row in self.board.fixed], #save which cells were fixed for replaying later
            "current_grid": self.board.copyGrid(), #save the current grid state for resuming later
            "moves": [state.toDict() for state in self.undoRedo.history()] #convert the move history to a list of dicts for json 
        }
        self.history.save(session) #save the session to the history file for replaying later

    def replayGame(self, session: dict):
        self.board = Board() #create a new blank board to replay the game on
        self.board.grid = copy.deepcopy(session["initial_board"]) #set the board to the initial state of the game
        self.board.fixed = copy.deepcopy(session["fixed_cells"]) #set which cells are fixed for the replay
        self.board.solution = copy.deepcopy(session["solution"]) #set the solution for the replay
        moves = session["moves"] #list of move dicts to replay in order
        #tot = len(moves)
        #start=time.time() #start the timer for the replay
        
        #print(f"{Colors.BOLD}{Colors.CYAN}Replaying Game from {session['timestamp']} - Difficulty: {session['difficulty'].upper()}{Colors.RESET}\n")
        
        for i, moveDict in enumerate(moves, start=1): #show the replay of what moves were made 
            self.board.setCell(moveDict['row'], moveDict['col'], moveDict['new_num']) #apply each move to the board
            self.display.clear()
            self.display.title()
            print(f"{Colors.BOLD}{Colors.CYAN}Replaying Game from {session['timestamp']} - Difficulty: {session['difficulty'].upper()}{Colors.RESET}\n")
            print(f"Move {i} of {len(moves)}\n")
            self.display.board(self.board) #display the board after each move is applied
            time.sleep(3) 
        
        self.display.clear()
        self.display.title()
        input("Replay complete! Press 'Enter' to return to the main menu...")

    def replay_as_new_game(self, session: dict): # load the same starting board but let the player solve it anew
        self.board = Board()
        self.board.grid = copy.deepcopy(session["initial_board"])
        self.board.fixed = copy.deepcopy(session["fixed_cells"])
        self.board.solution = copy.deepcopy(session["solution"])
        self.initialBoard = self.board.copyGrid()
        self.undoRedo = UndoRedo()
        self.freebieUsed = False
        self.mistakeCount = 0
        self.startTime = time.time()
        self.timeLimit = None
        difficulty = session.get("difficulty", "medium")
        self.gameLoop(difficulty)

    def resumeGame(self, session: dict):
        self.board = Board()
        self.board.grid = copy.deepcopy(session["current_grid"])  #picks up where you left off
        self.board.fixed = copy.deepcopy(session["fixed_cells"])
        self.board.solution = copy.deepcopy(session["solution"])
        self.initialBoard = copy.deepcopy(session["initial_board"])
        self.undoRedo = UndoRedo()
        self.freebieUsed = False
        self.mistakeCount = 0
        self.startTime = time.time() - session.get("elapsed", 0)
        self.timeLimit = None
        difficulty = session.get("difficulty", "medium")
        self.gameLoop(difficulty)

class Controller:
    def __init__(self):
        self.gameplay = SudokuGamePlay()
        self.display = Display()

    def run(self):
        while True:
            self.display.clear()
            self.display.title()
            self.display.menu()
            choice = input(f"{Colors.DIM}{Colors.MAGENTA}Select your choice: {Colors.RESET}").strip().lower()

            if choice == '1': # help text prompt
                self.display.clear()
                self.display.help_text()
            elif choice == '2': #start a new game prompt
                self.newGame()
            elif choice == '3':
                self.replay_menu() #replay previous game prompt, shows the list of saved game sessions and allows the user to select one to replay or replay as a new game
            elif choice == '4':
                self.history_menu() #view game history prompt, shows the list of saved game sessions with details but without the option to replay since it's just for viewing past performance and stats
            elif choice == '5': #quit the game
                print(f"{Colors.CYAN}Thanks for playing! {Colors.RESET}\n")
                break
            else:
                print(f"{Colors.RED}Invalid choice. Please try again.{Colors.RESET}")
                time.sleep(1)

    def newGame(self):
        while True:
            self.display.clear()
            self.display.difficulty_menu()
            choice = input(f"{Colors.DIM}{Colors.MAGENTA}Choose difficulty: {Colors.RESET}").strip().lower()

            time_lim = None   #only set a time limit if the user selects timed mode
            if choice == 'a': 
                self.gameplay.newGame("easy")
                return
            elif choice == 'b':
                self.gameplay.newGame("medium")
                return
            elif choice == 'c':
                self.gameplay.newGame("hard")
                return
            elif choice == 't':           
                diff_choice = input(f"{Colors.DIM}{Colors.MAGENTA}Choose difficulty for timed mode (a=easy, b=medium, c=hard): {Colors.RESET}").strip().lower()
                diff_map = {"a": "easy", "b": "medium", "c": "hard"}
                if diff_choice not in diff_map: #validate the difficulty choice for timed mode
                    print(f"{Colors.RED}Invalid difficulty choice.{Colors.RESET}")
                    time.sleep(1)
                    continue
                timeLimit = input(f"{Colors.DIM}{Colors.MAGENTA}Enter time limit in minutes: {Colors.RESET}").strip()
                try:
                    time_limit = int(timeLimit) * 60 #convert minutes to seconds for the game timer
                    self.gameplay.newGame(diff_map[diff_choice], time_limit)
                    return
                except ValueError:
                    print(f"{Colors.RED}Invalid time limit. Please enter a number.{Colors.RESET}")
                    time.sleep(1)
            elif choice == 'q': #go back to main menu
                return
            else:
                print(f"{Colors.RED}Invalid choice. Please try again.{Colors.RESET}")

            # diff_map = {"a": "easy", "b": "medium", "c": "hard", "t": "timed"}
            # if choice not in diff_map:
            #     difficulty = "medium" #default to medium if invalid choice somehow gets through
            
            # self.gameplay.newGame(diff_map[choice], time_limit = time_lim)
            # return
        
    def replay_menu(self):
        sessions = self.gameplay.history.listSessions() #get the list of saved game sessions for replaying
        if not sessions: #no saved sessions, return to main menu 
            self.display.clear()
            self.display.title()
            print(f"{Colors.DIM}No game history available to replay.{Colors.RESET}")
            input("Press 'Enter' to return to the main menu...")
            return
        
        while True:
            self.display.clear()
            self.display.title()
            print(f"{Colors.BOLD}{Colors.CYAN}Game History:{Colors.RESET}\n")
            for i, session in enumerate(sessions, start=1): #present the list of saved sessions with details for the user to select which one to replay
                timestamp = session.get('timestamp', 'Unknown')
                difficulty = session.get('difficulty', 'unknown')
                completed = "Completed" if session.get('completed', False) else "Incomplete"
                elapsed = session.get('elapsed', 0)
                mins = int(elapsed) // 60
                secs = int(elapsed) % 60
                print(f"{i}. {timestamp} - Difficulty: {difficulty.upper()} - {completed} - Time: {mins:02d}:{secs:02d}")
            choice = input(f"\n{Colors.DIM}{Colors.MAGENTA}Enter the number of the game to replay or 'q' to return to the main menu: {Colors.RESET}").strip().lower()
            if choice == 'q': # go back to menu
                return
            
            try: #validate the input and replay the selected game session
                index = int(choice) - 1 #convert to 0 indexing
                if 0 <= index < len(sessions): #valid index, proceed to replay
                    session = sessions[index]
                    print("\nWhat would you like to do?")
                    print("1. Watch playback of this game")
                    print("2. Replay the same board from scratch")
                    print("3. Resume from where you left off") 
                    mode = input(f"{Colors.DIM}{Colors.MAGENTA}Choose (1, 2, or 3): {Colors.RESET}").strip()
                    if mode == '1':
                        self.gameplay.replayGame(session)
                    elif mode == '2':
                        self.gameplay.replay_as_new_game(session)
                    elif mode == '3':
                        self.gameplay.resumeGame(session) 
                    else: #invalid choice for replay mode, return to replay menu
                        print(f"{Colors.RED}Invalid choice.{Colors.RESET}")
                        time.sleep(1)
                    break
                else: #invalid index, prompt again
                    print(f"{Colors.RED}Invalid choice. Please enter a number between 1 and 3.{Colors.RESET}")
                    time.sleep(1)
            except ValueError: #cannot be converted to an integer, prompt again
                print(f"{Colors.RED}Invalid input. Please enter a number or 'q'.{Colors.RESET}")
                time.sleep(1)
    
    def history_menu(self):
        sessions = self.gameplay.history.listSessions() #get the list of saved game sessions for viewing
        self.display.clear()
        self.display.title()

        if not sessions:
            print(f"{Colors.DIM}No game history available.{Colors.RESET}")
            input("Press 'Enter' to return to the main menu...")
            return
        
        print(f"{Colors.BOLD}{Colors.CYAN}Game History:{Colors.RESET}\n") #same as replay menu but without the option to select a game for replaying since this is just for viewing past performance and stats, not for replaying
        for i, session in enumerate(sessions, start=1):
            timestamp = session.get('timestamp', 'Unknown')
            difficulty = session.get('difficulty', 'unknown')
            completed = "Completed" if session.get('completed', False) else "Incomplete"
            elapsed = session.get('elapsed', 0)
            mins = int(elapsed) // 60
            secs = int(elapsed) % 60
            print(f"{i}. {timestamp} - Difficulty: {difficulty.upper()} - {completed} - Time: {mins:02d}:{secs:02d}")
        
        input("\nPress 'Enter' to return to the main menu...")

if __name__ == "__main__": #entry point of the program, creates a Controller instance and starts the main loop
    Controller().run()