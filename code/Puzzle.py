# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 16:59:25 2021

@author: yigit
"""

import numpy as np


class Puzzle():
    def __init__(self, clues, corner_numbers, black_cells, date="TODO: add date functionality"):
        self.date = date
        
        
        self.corner_numbers = np.array(corner_numbers).reshape((5,5))
        self.black_cells = np.array(black_cells).reshape((5,5))
        
        
        self.accross_constraints = []
        self.down_constraints = []
        for i in range(5):
            print(i)
            start_flag = False
            start_pos = -1
            length = -1
            for j in range(5):
                if start_flag:
                    if self.black_cells[i][j] == 1:
                        length = j - start_pos
                        self.accross_constraints.append((start_pos, length))
                        break
                    elif j == 4:
                        length = 5 - start_pos
                        self.accross_constraints.append((start_pos, length))
                else:
                    if self.black_cells[i][j] == 0:
                        start_flag = True
                        start_pos = j
                        
                        
        for i in range(5):
            start_flag = False
            start_pos = -1
            length = -1
            for j in range(5):
                if start_flag:
                    if self.black_cells[j][i] == 1:
                        length = j - start_pos
                        self.down_constraints.append((start_pos, length))
                        break
                    elif j == 4:
                        length = 5 - start_pos
                        self.down_constraints.append((start_pos, length))
                else:
                    if self.black_cells[j][i] == 0:
                        start_flag = True
                        start_pos = j
                        
        accross_clues = clues[0]
        down_clues = clues[1]
        
        # reorder accross clues from top to bottom
        order = []
        texts = []
        for i in range(5):
            corner_number = int(accross_clues[2*i])
            texts.append(accross_clues[2*i+1])
            
            start_pos = self.get_start_pos(corner_number)
            order.append(start_pos[0])

        i = 0
        while i < 5:
            if order[i] != i:
                temp = order[order[i]]
                temp_2 = texts[order[i]]
                order[order[i]] = order[i]
                texts[order[i]] = texts[i]
                order[i] = temp
                texts[i] = temp_2
            else:
                i += 1
                
        accross_clues = texts
        
        print(texts)
                
        
        # reorder down clues from left to right
        order = []
        texts = []
        for i in range(5):
            corner_number = int(down_clues[2*i])
            texts.append(down_clues[2*i+1])
            
            start_pos = self.get_start_pos(corner_number)
            order.append(start_pos[1])
            
        i = 0
        while i < 5:
            if order[i] != i:
                temp = order[order[i]]
                temp_2 = texts[order[i]]
                order[order[i]] = order[i]
                texts[order[i]] = texts[i]
                order[i] = temp
                texts[i] = temp_2
            else:
                i += 1
        
        down_clues = texts
        print(texts)

        self.clues = (accross_clues, down_clues)

    def get_start_pos(self, corner_number):
        pos = np.where(self.corner_numbers == corner_number)
        return pos[0][0], pos[1][0]
    
    def get_constraints(self):
        constraints = []
        for acc_idx in range(5):
            for down_idx in range(5):
                acc_start = self.accross_constraints[acc_idx][0]
                down_start = self.down_constraints[down_idx][0]
                
                acc_len = self.accross_constraints[acc_idx][1]
                down_len = self.down_constraints[down_idx][1]
                
                # calculate if its in the boundaries of the entries
                if (down_idx >= acc_start and acc_idx >= down_start
                    and down_idx < acc_start + acc_len
                    and acc_idx < down_start + down_len):
                    # if it is, add the constraint to list
                    
                    acc_at = down_idx - acc_start
                    down_at = acc_idx - down_start
                    
                    constr = (acc_idx, acc_at, down_idx, down_at)
                    constraints.append(constr)
                        
        return constraints
        
        
class Clue():
    def __init__(self, text, start_pos, direction):
        self.text = text
        self.start_pos = start_pos
        
        # for direction 0->accross, 1->down
        self.direction = direction