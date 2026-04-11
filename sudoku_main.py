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


