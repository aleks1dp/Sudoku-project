import random #unique numbers each game
import time #timer function of the game
import copy #creates a copy for gameplay to retain the original solution
import json #saves and loads game state
import os #checks whether a save file exists
from collections import deque #used for backtracking algorithm
from datetime import datetime #used for timestamping save files

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
    size = 9
    base = 3

    #helper function for initialzing the grid and fixed arrays
    def create_grid(self): 
        return [[0 for  _ in range(self.size)] for _ in range(self.size)]

    def __init__(self):
        self.grid = self.create_grid(0) #empty grid of 9x9
        self.fixed = self.create_grid(False) #player is not allowed to change these cells if changed to True boolean array to track which cells are fixed
        self.solution = [] #copy of the completed grid to check against player's input

    def row_valid(self, row: int, num: int, col_exclude: int = -1) -> bool:
        for c in range(self.size):
            if c == col_exclude:
                continue
            if self.grid[row][c] == num: #if the number is found in the same row, it's not valid
                return False
        return True #otherwise it's valid
    
    def col_valid(self, col: int, num: int, row_exclude: int = -1) -> bool:
        for r in range(self.size):
            if r == row_exclude:
                continue
            if self.grid[r][col] == num: #if the number is found in the same column, it's not valid
                return False
        return True #otherwise it's valid
    
    def box_valid(self, row: int, col: int, num: int, row_exclude: int = -1, col_exclude: int = -1) -> bool:
        box_row_start = (row // self.base) * self.base # starting point example row 5 so 5/3=1 
                                                        # then 1*3 = 3 so the top of the 3x3 box is 3
        box_col_start = (col // self.base) * self.base
        for r in range(box_row_start, box_row_start + self.base):
            for c in range(box_col_start, box_col_start + self.base):
                if (r, c) != (row_exclude, col_exclude): # skip the cell we are placing into -- don't conflict with itself
                    if self.grid[r][c] == num: #if the number is found in the same 3x3 box, it's not valid
                        return False
        return True #otherwise it's valid
    
    def is_valid(self, row: int, col: int, num: int) -> bool: # checks for all three conditions for a valid placement
        return self.row_valid(row, num, col) and self.col_valid(col, num, row) and self.box_valid(row, col, num, row, col)
    
    def is_cell_fixed(self, row: int, col: int) -> bool:
        return self.fixed[row][col] #has a value that player cannot change
    
    def set_cell(self, row: int, col: int, num: int, fixed: bool = False):
        self.grid[row][col] = num #sets the value of the cell to the number provided
        self.fixed[row][col] = fixed #if fixed is True, player cannot change this cell

    def get_cell(self, row: int, col: int) -> int:
        return self.grid[row][col] #returns the value of the cell

    def complete(self) -> bool:
        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row][col] == 0: #if any cell is empty, the board is not complete
                    return False
                if self.solution and self.grid[row][col] != self.solution[row][col]: #checks whether filled incorrectly
                    return False
        return True #otherwise it's complete
    
    def remaining_cells(self) -> dict:
        placed = {n: 0 for n in range(1, self.size + 1)} #dictionary to count how many of each number has been placed
        for row in range(self.size): # counts how many times a number is on the 9x9 grid and updates the dictionary accordingly
            for col in range(self.size):
                if self.grid[row][col] != 0:
                    placed[self.grid[row][col]] += 1
        return placed
    
    def copy_grid(self):
        return copy.deepcopy(self.grid) #creates a  copy of the grid to retain the original solution for checking against player's input
    


    class SudokuGenerator:
        CLUES = {1: 40, 2: 32, 3: 25} #number of clues for each difficulty level

        def generate(self, difficulty: str):
            self.board = Board() #creates a blank board
            self.fill(self.board.grid) 
            self.board.solution = self.board.copy_grid() #saves the completed grid as the solution before removign cells depending on the difficulty level
            self.remove_cells(self.board, difficulty) #removes cells based on the difficulty

            for row in range(self.board.size):
                for col in range(self.board.size): 
                    self.board.fixed[row][col] = (self.board.grid[row][col] != 0) #every cell that is not empty is marked as fixed so the player cannot change it
            return self.board 
        
    def fill(self, grid: list) -> bool:
        for row in range(Board.size):
            for col in range(Board.size):
                if grid[row][col] == 0: #finds the first empty cell
                    numbers = list(range(1, Board.size + 1)) #1-9 numbers to try placing in the cell
                    random.shuffle(numbers) #randomize the 1-9 numbers
                    for num in numbers:
                        if self.is_valid(row, col, num): #checks if placing the number is valid 
                            grid[row][col] = num #places the number in the cell
                            if self.fill(grid): #fill remaining cells 
                                return True
                            grid[row][col] = 0 #backtracks if it leads to an invalid state
                    return False #if no number can be placed, backtrack
        return True #if the grid is completely filled, return True
    
    @staticmethod #helps with organizaition since this function is only used for generating the board and doesn't rely on any instance variables
    def is_valid(grid: list, row: int, col: int, num: int) -> bool:
        if num in grid[row]: #check row
            return False
        if any(grid[r][col] == num for r in range(Board.size)): #check column -- look at the same column in every row to see if the number is present
            return False
        box_row_start = (row // Board.base) * Board.base # 0 3 or 6
        box_col_start = (col // Board.base) * Board.base
        for r in range(box_row_start, box_row_start + Board.base):
            for c in range(box_col_start, box_col_start + Board.base):
                if grid[r][c] == num:
                    return False
        return True # if num is not found in the row, column, or 3x3 box, it's valid to place it there
    
    def remove_cells(self, board: Board, difficulty: str):
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

            test_board = copy.deepcopy(board) #create a copy of the board to test if it still has a unique solution after removing the cell
            count = self.count_solutions(test_board) #count the number of solutions for the test board
            if count != 1: #if the test board does not have a unique solution
                board.grid[row][col] = fail_safe #restore the original value
            else:
                removed += 1 #keep the removal as the sol is unique and increment the count of removed cells

    def count_solutions(self, grid: list[list[int]], limit: int = 2) -> int: #2 or more solutions = not unique
        solutions = 0

        for row in range(Board.size):
            for col in range(Board.size):
                if grid[row][col] == 0: #empty cell
                    for num in range(1, Board.size + 1): # go from 1-9 to try placing in the empty cell
                        if self.is_valid(grid, row, col, num): #check if placing the number is valid
                            grid[row][col] = num 
                            solutions += self.count_solutions(grid, limit) #recur to count solutions for the remaining cells
                            grid[row][col] = 0 #backtrack
                            if solutions >= limit: #no empty cells found, stop searching
                                return solutions
                    return solutions #return the number of solutions found so far
                


class GameState:
    __slots__ = ("row", "col", "num", "timestamp") #only allows these attributes for each GameState instance

    def __init__(self, row: int, col: int, old_num: int, new_num: int):
        self.row = row
        self.col = col
        self.old_num = old_num # before move (undo functionality)
        self.new_num = new_num # after move (redo/replay fucntionality)
        self.timestamp = time.time() #when this happened during gameplay

    def to_dict(self)-> dict: #converts to dict for json serialization when saving the game state to a file
        return {
            "row": self.row,
            "col": self.col,
            "old_num": self.old_num,
            "new_num": self.new_num,
            "timestamp": self.timestamp
        }
    
class UndoRedo:
    def __init__(self):
        self.undo: list  = []
        self.redo: list = []

    def push(self, state: GameState):
        self.undo.append(state) #add the new game state to the undo stack
        self.redo.clear() #clear the redo stack since we can only redo immediately after an undo
    
    def undo(self) -> GameState:
        if not self.undo:
            return None 
        state = self.undo.pop() #most recent game state from the undo stack
        self.redo.append(state) #add it to the redo stack 
        return state 
    
    def redo(self) -> GameState:
        if not self.redo:
            return None 
        state = self.redo.pop() #most recent game state from the redo stack
        self.undo.append(state) #add it back to the undo stack since we are redoing it
        return state
    
    def can_undo(self) -> bool: 
        return bool(self.undo) #1+ move that cna be undone
    
    def can_redo(self) -> bool:
        return bool(self.redo) #1+ move that can be redone
    
    def history(self) -> list:
        return self.undo + self.redo[::-1] #combine undo and redo stacks to show full history of moves, with undo moves in order and redo moves in reverse order since they are undone moves
    
    def clear(self): #cleared at the stat of a new game to reset the move history
        self.undo.clear() 
        self.redo.clear()

    
HISTORY_FILE = "sudoku_history.json" #file to save the move history for replay functionality

class SudokuGameHistory:
    def __init__(self):
        self.sessions: list = self.load() # load previously saved sessions if any available

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
    
    def list_sessions(self)->list:
        return self.sessions #return the list of saved sessions for replaying past games
    
    def get_session(self, index: int) -> dict:
        if 0 <= index < len(self.sessions):
            return self.sessions[index] #return the session at the specified index if it exists
        return None #invalid index -- out of bound --  return None
    

class Display:
    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear') #clear between moves for better readability

    @staticmethod
    def title():
        print(f"""{Colors.BOLD}{Colors.BLUE}Welcome to Sudoku!{Colors.RESET}\n{Colors.DIM}  Classic 9x9  |  Undo/Redo  |  Replay  |  Timed Mode{Colors.RESET}""") 
    
    @staticmethod
    def board(board, highlight=None, mistakes = None, elapsed = None, time_limit = None):

        #timer on top right of the board
        if elapsed is not None:
            mins, secs = divmod(elapsed, 60)
            timer = f"Timer: {int(mins):02d}:{int(secs):02d}"

            if time_limit is not None:
                remaining_time = max(0, time_limit - elapsed)
                mins_remain, secs_remain = divmod(remaining_time, 60)
                timer += f" | Remaining: {int(mins_remain):02d}:{int(secs_remain):02d}"
            print(f"{Colors.BOLD}{Colors.YELLOW}{timer}{Colors.RESET}\n")

            size = board.size

        #Column headers
        print(f"\n{Colors.DIM}    1 2 3 | 4 5 6 | 7 8 9{Colors.RESET}")
        print(f"{Colors.DIM}   ───────────────────────{Colors.RESET}")

        #Rows of the board
        for row in range(size):
            if row > 0 and row % board.base == 0:
                print(f"{Colors.DIM}   ───────────────────────{Colors.RESET}")
            row_str = f"{Colors.DIM} {row + 1} │{Colors.RESET}"
            for col in range(size):
                cell_value = board.get_cell(row, col)
                cell_str = f"{cell_value}" if cell_value != 0 else " " #empty cells are shown as blank spaces
                if highlight and (row, col) in highlight:
                    colors = colors.YELLOW + colors.BOLD #highlight hinted cells in yellow
                elif mistakes and (row, col) in mistakes:
                    colors = colors.RED + colors.BOLD #highlight incorrect cells in red
                elif board.is_cell_fixed(row, col):
                    colors = colors.WHITE + colors.BOLD #clues are highlighted in white
                elif cell_value != 0:
                    colors = colors.BLUE + colors.BOLD #player's correct inputs are highlighted in blue
                else:
                    colors = colors.DIM #empty cells are dimmed to differentiate them from filled cells
                row_str += f" {colors}{cell_str}{Colors.RESET}"
                if col in [2, 5]: #vertical separators for 3x3 boxes
                    row_str += f" {Colors.DIM}|{Colors.RESET}"
                else:
                    row_str += " " #regular space between cells
            print(row_str)
        
        print(f"\n{Colors.DIM}   ───────────────────────{Colors.RESET}")

        @staticmethod
        def rem_numbers(board: Board):
            remaining = board.remaining_cells() #get the count of how many of each number has been placed on the board
            print(f"\n{Colors.MAGENTA}{Colors.BOLD}Numbers Remaining:{Colors.RESET}")
            for num in range(1, board.size + 1):
                count = remaining[num] #how many have been placed
                if count == 0:
                   colors = Colors.GREEN + Colors.BOLD #if none have been placed, green to show it's a good number to place
                elif count <= 3:
                    colors = Colors.YELLOW + Colors.BOLD 
                else:
                    colors = Colors.WHITE + Colors.BOLD #most are still needed
                line += f"{colors}{num}:{Colors.RESET} {count}" #show the number and how many have been placed
            print(line +"\n")

        @staticmethod
        def menu():
            print("\n=== MAIN MENU ===")
            print("1. How to Play")
            print("2. New Game")
            print("3. Replay Previous Game")
            print("4. View Game History")
            print("5. Quit")

        @staticmethod
        def difficulty_menu():
            print("\nSelect Difficulty:")
            print("a. Easy   (40 clues)")
            print("b. Medium (32 clues)")
            print("c. Hard   (25 clues)")
            print("t. Timed Mode")
            print("x. Back")

        @staticmethod
        def how_to_play():
            print("\n=== HOW TO PLAY ===")
            print("Fill the 9x9 grid so each row, column, and 3x3 box")
            print("contains the digits 1–9 exactly once.\n")
            print("Enter moves as: row col digit  (e.g., 3 5 7)")
            print("Clear a cell: row col 0")
            print("u - Undo last move")
            print("r - Redo an undone move")
            print("h - Hint")
            print("s - Show remaining numbers")
            print("q - Quit the game")
            input("\nPress 'Enter' to continue...")



class SudokuGamePlay:
    def __init__(self):
        self.board = None
        self.undo_redo = UndoRedo()
        self.history = SudokuGameHistory()
        self.display = Display()
        self.generator = Board.SudokuGenerator()
        self.start_time = 0.0
        self.time_limit = None

    def new_game(self, difficulty: str, time_limit: int = None):
        self.board = self.generator.generate(difficulty) #new board based on the selected difficulty
        self.undo_redo = UndoRedo()#clear the undo redo history 
        self.start_time = time.time() #start the timer
        self.time_limit = time_limit #set the time limit
        self.game_loop() #start the game loop for player input and interaction

        def game_loop(self, difficulty: str):
            mistakes = set() #track incorrect placements to highlight them on the board
            while True:
                self.display.clear()
                self.display.title()
                elapsed = time.time() - self.start_time #calculate elapsed time
                
                difficulty_color = {
                    "easy": Colors.GREEN,
                    "medium": Colors.YELLOW,
                    "hard": Colors.RED,
                    "timed": Colors.MAGENTA
                }.get(difficulty, Colors.WHITE) 

                print(
                f" Difficulty: {difficulty_color}{difficulty.upper()}{Colors.RESET}  "
                f"|  Undo: "{Colors.GREEN if self.move_stack.can_undo() else Colors.DIM}"
                f"{'YES' if self.move_stack.can_undo() else 'no'}{Colors.RESET}  "
                f"|  Redo: "{Colors.GREEN if self.move_stack.can_redo() else Colors.DIM}"
                f"{'YES' if self.move_stack.can_redo() else 'no'}{Colors.RESET}\n"
                )

                self.display.board(self.board, mistakes = mistakes, elapsed=elapsed, time_limit=self.time_limit) #display the board with the timer and time limit if in timed mode
                self.display.rem_numbers(self.board) #show how many of each number have been placed and how many are remaining

            
                if self.time_limit and elapsed >= self.time_limit: #check if time limit has been reached
                    print(f"{Colors.RED}{Colors.BOLD}Time's up! Game over.{Colors.RESET}\n")
                    self.save_history(difficulty, completed = False, elapsed=elapsed) #save the game history even if they didn't finish for replaying later
                    input("Press 'Enter' to return to the main menu...")
                    return #return to main menu after time's up

                if self.board.complete(): #check if the board is complete after each move
                    elapsed = time.time() - self.start_time #final elapsed time
                    self.display.clear()
                    self.display.title()
                    self.display.board(self.board)
                    mins, secs = divmod(elapsed, 60)
                    print(f"{Colors.GREEN}{Colors.BOLD}Congratulations! You solved the puzzle in {mins:02d} minutes and {secs:02d} seconds!{Colors.RESET}\n")
                    self.save_history(difficulty, completed=True, elapsed=elapsed) #save the game history
                    input("Press 'Enter' to return to the main menu...")
                    return

                # Player input handling
                print("Enter your move (row col num), or 'u' to undo, 'r' to redo, 'h' for hint, 's' for remaining numbers, 'q' to quit")

                try:
                    raw_input = input().strip().lower() #get player input and normalize it
                except:
                    raw_input = "q" #if input fails, treated as a quit command to avoid crashing
                
                if raw_input == 'q': #quit the game
                    self.save_history(difficulty, completed=False, elapsed=time.time()-self.start_time) #save the game history
                    print(f"{Colors.YELLOW}Game saved. Returning to main menu...{Colors.RESET}\n")
                    time.sleep(1)
                    return
                
                if raw_input == 'u': #undo the last move
                    self.undo_move(mistakes)
                    continue

                if raw_input == 'r': #redo the last undone move
                    self.redo_move(mistakes)
                    continue    

                if raw_input == 'h': #provide a hint by filling in one of the empty cells with the correct value from the solution
                    self.hint(mistakes)
                    continue

                if raw_input == 's': #show how many of each number have been placed and how many are remaining
                    input("Press 'Enter' to continue...")
                    continue 

            
            #Verifying inputs
        




