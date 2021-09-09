# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 18:59:45 2021

@author: yigit
"""

# Function that returns across clues and down clues as two lists
def get_clues( brwsr ):
    # reveal answers using the xpaths of the buttons on nyt's webpage
    brwsr.find_elements_by_xpath('//*[@id="root"]/div/div/div[4]/div/main/div[2]/div/div/ul/div[2]/li[2]/button')[0].click()
    print("ACTION: Clicked 'Reveal'")
    brwsr.find_elements_by_xpath('//*[@id="root"]/div/div/div[4]/div/main/div[2]/div/div/ul/div[2]/li[2]/ul/li[3]/a')[0].click()
    print("ACTION: Clicked 'Puzzle'")
    brwsr.find_elements_by_xpath('//*[@id="root"]/div/div[2]/div[2]/article/div[2]/button[2]/div')[0].click()
    print("ACTION: Clicked 'Reveal'")
    brwsr.find_elements_by_xpath('//*[@id="root"]/div/div[2]/div[2]/span')[0].click()
    print("ACTION: Clicked 'X'")
    
    # extract across and down clues
    clues_across = brwsr.find_elements_by_xpath('//*[@id="root"]/div/div/div[4]/div/main/div[2]/div/article/section[2]/div[1]/ol')[0].text.split('\n')
    clues_down = brwsr.find_elements_by_xpath('//*[@id="root"]/div/div/div[4]/div/main/div[2]/div/article/section[2]/div[2]/ol')[0].text.split('\n')

    return clues_across, clues_down

# Function that returns corner numbers and answer letters of puzzle grid as two lists
def get_puzzle_data( brwsr ):
    data = []
    # getting the grid data using css selector
    for index in range(25):
        selector = "#xwd-board > g:nth-child(5) > g:nth-child(" + str( index + 1 ) + ")"
        if brwsr.find_elements_by_css_selector( selector ):
            data.append( brwsr.find_elements_by_css_selector( selector )[0].text.split('\n') )
        else:
            data.append('')
            
    # we will have two arrays, one for the corner numbers one for the answer letters in the grid
    puzzle_numbers = []
    puzzle_letters = []
    black_cells = []
    
    print(data)

    for i, cell in enumerate(data):
        if len(cell) == 3:
            data[i] = cell[1:]
            
    for i, cell in enumerate(data):
        if len(cell) == 2 and cell[0] > '9':
            data[i] = cell[1:]

    print(data)    

    # filling the letters and numbers arrays (mentioned right above)
    for cell in data:
        # the cell has a number and letter inside
        if len(cell) == 2: 
            puzzle_numbers.append(int(cell[0])) # corner number
            puzzle_letters.append(cell[1]) # answer letter
            if cell[1] == '':
                black_cells.append(1)
            else:
                black_cells.append(0)
        # the cell has only a letter inside
        else:
            puzzle_numbers.append(0) # corner number will be empty string
            puzzle_letters.append(cell[0]) # answer letter, will be empty string if cell is black
            if cell[0] == '':
                black_cells.append(1)
            else:
                black_cells.append(0)
                
    
            
    return puzzle_numbers, puzzle_letters, black_cells
        