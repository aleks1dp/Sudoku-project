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
    


    class SudokuGame:
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

