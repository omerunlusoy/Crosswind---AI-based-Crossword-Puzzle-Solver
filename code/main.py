# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 16:40:21 2021

@author: yigit
"""
from time import sleep

from common import show_browser, test_mode
import pickle

from selenium import webdriver
from nyt_scraper import get_clues, get_puzzle_data
from Puzzle import Puzzle
from candidate_generator import CandidateGenerator
from word_scraper import WikiGoogleScraper, WebsterScraper, SynonymsScraper, Webster_Dic_Scraper, Webster_Dic_Whole_Scraper, Wikipedia_Main_Page_Scrapper, \
    Wikipedia_Main_Page_Entire_Clue_Scrapper
from solver import solve_for
import sys
from tkinter import Frame, Canvas, scrolledtext, Label, font, BOTH, LEFT, TOP, END
from tkinter import Tk
from datetime import date, datetime
import numpy as np
import os

# Global variables -----------------------------------------------------------
color = "black"                                 # color for all text and puzzle grid
group_name = "CROSSWIND" 
MARGIN = 15                                     # Pixels around the puzzle grid
SIDE = 70                                       # Width of every board cell.
WIDTH = HEIGHT = MARGIN * 2 + SIDE * 6 + 30     # Width and height of the whole grid
CLUESHEIGHT = WIDTH - 50                        # height of ui element
CLUESWIDTH = WIDTH * 1.25                       # width of ui element
bottom_text = ""                                # the text below the grid (will have date, time, group name)
circles = np.zeros(25)

# UI elements ----------------------------------------------------------------

link2 = "https://www.nytimes.com/crosswords/game/special/tricky-clues-mini"
link3 = "https://www.nytimes.com/crosswords/game/special/themed-mini"
link4 = "https://www.nytimes.com/crosswords/game/special/pets-mini"
link5 = "https://www.nytimes.com/crosswords/game/mini/tips-and-tricks/themes"

link = "https://www.nytimes.com/crosswords/game/mini/2021/04/14"


# a Frame that contains the puzzle grid and a bottom text for time and group name
class PuzzleFrame(Frame):
    def __init__(self, parent, bottom_text, MARGIN, SIDE, bgcolor, numbers, letters, top_text):
        Frame.__init__(self, parent)
        self.parent = parent
        self.bottom_text = bottom_text
        self.top_text = top_text
        self.MARGIN = MARGIN
        self.SIDE = SIDE
        self.bgcolor = bgcolor
        self.numbers = numbers
        self.letters = letters
        self.__initUI()

    def __initUI(self):
        self.parent.title("CROSSWIND")
        self.pack(fill=BOTH, side=LEFT)
        self.WIDTH = self.MARGIN * 2 + self.SIDE * 5
        self.HEIGHT = self.WIDTH + 25
        self.canvas = Canvas(self,
                             width=self.WIDTH,
                             height=self.HEIGHT+10)
        self.canvas.pack(fill=BOTH, side=TOP)
        self.__draw_grid()
        self.__draw_puzzle()

    # draw bottom text and the puzzle grid that will contain the answers
    def __draw_grid(self):
        
        self.__draw_top_text()
        
        # paint puzzle grid's inside white
        self.canvas.create_rectangle(
            self.MARGIN, self.MARGIN + 25, 
            self.MARGIN + self.SIDE*5, self.MARGIN + self.SIDE*5 + 25, 
            fill='white'
            )
        
        self.__draw_bottom_text()
        
        # draw the lines that make up the puzzle grid
        for i in range(6):
            width = 1  # width of drawn line
            if i == 0 or i == 5:
                width = 3  # bold lines for the edges of the puzzle grid

            x0 = self.MARGIN + self.SIDE*i
            y0 = self.MARGIN + 25
            x1 = self.MARGIN + self.SIDE*i
            y1 = self.HEIGHT - self.MARGIN
            self.canvas.create_line(x0, y0, x1, y1, fill=color, width=width)

            x0 = self.MARGIN
            y0 = self.MARGIN + self.SIDE*i + 25
            x1 = self.WIDTH - self.MARGIN
            y1 = self.MARGIN + self.SIDE*i + 25
            self.canvas.create_line(x0, y0, x1, y1, fill=color, width=width)
            
        for i in range(25):
            if circles[i] == 1:
                row = int(i / 5)
                col = i % 5
                x0 = self.MARGIN + col*self.SIDE
                x1 = x0 + self.SIDE
                y0 = self.MARGIN + row*self.SIDE + 25
                y1 = y0 + self.SIDE
                self.canvas.create_oval( x0, y0, x1, y1 )
         
    # draw black squares, corner numbers and answer letters on the puzzle grid
    def __draw_puzzle(self):
        letterfont = font.Font(size=24, weight="bold")
        cornerfont = font.Font(size=11, weight="bold")
        for i in range(5):
            for j in range(5):
                answer = self.letters[i*5+j]
                number = self.numbers[i*5+j]
                
                if answer != '':  # cell is not black
                    # calculate cell center
                    x = self.MARGIN + j * self.SIDE + self.SIDE / 2
                    y = self.MARGIN + i * self.SIDE + self.SIDE / 2 + 25
                    # draw answer letter in cell center
                    self.canvas.create_text(
                        x, y, text=answer, tags="numbers", fill=color, font=letterfont
                        )
                    
                    if number != '':  # draw the corner number if it exists
                        self.canvas.create_text(
                            x-27, y-25, text=number, fill=color, font=cornerfont
                            )
                        
                else:  # cell is black
                    # paint the cell black
                    self.canvas.create_rectangle(
                        self.MARGIN+self.SIDE*j, 
                        self.MARGIN+self.SIDE*i + 25, 
                        self.MARGIN+self.SIDE*(j+1), 
                        self.MARGIN+self.SIDE*(i+1) + 25, 
                        fill=color
                        )
    
    def __draw_bottom_text(self):
        # clear previously drawn bottom text
        self.canvas.create_rectangle(
            self.MARGIN, self.MARGIN + self.SIDE*5 + 3 + 25, 
            self.MARGIN + self.SIDE*5.5, self.MARGIN + self.SIDE*5 + 30 + 25, 
            fill=self.bgcolor, outline=self.bgcolor
            )

        # draw the bottom text
        self.canvas.create_text(
            self.WIDTH-5*len(str(self.bottom_text)), self.HEIGHT, 
            text=self.bottom_text, font=("Arial",12)
            )

             
    def __draw_top_text(self):
        # # clear previously drawn top text
        # self.canvas.create_rectangle(
        #     5, self.MARGIN + 3, 
        #     self.SIDE*5.5 + 5, self.MARGIN + 30, 
        #     fill=self.bgcolor, outline=self.bgcolor
        #     )
        # draw the top text
        self.canvas.create_text(
            self.MARGIN+self.WIDTH/2, 15, 
            text=self.top_text, font=("Arial",12,"bold")
            )
        
    # updates bottom text and triggers redraw
    def set_bottom_text(self, bottom_text):
        self.bottom_text = bottom_text
        self.__draw_bottom_text()


# a Frame that contains two textboxes which will display clues
class CluesFrame(Frame):
    def __init__(self, parent, WIDTH, HEIGHT, across_clues, down_clues):
        Frame.__init__(self, parent, width=WIDTH, height=HEIGHT)
        self.parent = parent
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.across_clues = across_clues
        self.down_clues = down_clues
        self.__initUI()
        
    def __initUI(self):
        self.pack(fill=BOTH, side=LEFT)

        # frames that will contain the textboxes for clues
        acrossFrame = Frame(self, height=self.HEIGHT, width=self.WIDTH/2)
        acrossFrame.pack(side=LEFT, ipadx=10)
        downFrame = Frame(self, height=self.HEIGHT, width=self.WIDTH/2)
        downFrame.pack(side=LEFT, ipadx=10)
        
        # bold titles top left of textboxes
        Label(acrossFrame, text="ACROSS", font = "Helvetica 10 bold").place(x=10, y=0)
        Label(downFrame, text="DOWN", font = "Helvetica 10 bold").place(x=10, y=0)
        
        # textboxes to display clues
        acrossText = scrolledtext.ScrolledText(acrossFrame, width=36,font=("Arial",10))
        downText = scrolledtext.ScrolledText(downFrame, width=36,font=("Arial",10))
        
        # insert clues to text boxes
        for i in range(len(self.across_clues) // 2):
            acrossText.insert(END, " " + self.across_clues[2*i] + " ")
            acrossText.insert(END, self.across_clues[2*i + 1] + "\n\n")
        for i in range(len(self.down_clues) // 2):
            downText.insert(END, " " + self.down_clues[2*i] + " ")
            downText.insert(END, self.down_clues[2*i + 1] + "\n\n")
            
        # place textboxes in frame and disable editing
        acrossText.place(x=10, y=30)
        acrossText.config(state='disabled')
        downText.place(x=10, y=30)
        downText.config(state='disabled')


# Helper functions -----------------------------------------------------------

# Function that returns across clues and down clues as two lists
def get_clues(brwsr):
    # # reveal answers using the xpaths of the buttons on nyt's webpage
    # brwsr.find_elements_by_xpath('//*[@id="root"]/div/div/div[4]/div/main/div[2]/div/div/ul/div[2]/li[2]/button')[0].click()
    # #print("ACTION: Clicked 'Reveal'")
    # brwsr.find_elements_by_xpath('//*[@id="root"]/div/div/div[4]/div/main/div[2]/div/div/ul/div[2]/li[2]/ul/li[3]/a')[0].click()
    # #print("ACTION: Clicked 'Puzzle'")
    # brwsr.find_elements_by_xpath('//*[@id="root"]/div/div[2]/div[2]/article/div[2]/button[2]/div')[0].click()
    # #print("ACTION: Clicked 'Reveal'")
    # brwsr.find_elements_by_xpath('//*[@id="root"]/div/div[2]/div[2]/span')[0].click()
    # #print("ACTION: Clicked 'X'")
    
    # extract across and down clues
    clues_across = brwsr.find_elements_by_xpath('//*[@id="root"]/div/div/div[4]/div/main/div[2]/div/article/section[2]/div[1]/ol')[0].text.split('\n')
    clues_down = brwsr.find_elements_by_xpath('//*[@id="root"]/div/div/div[4]/div/main/div[2]/div/article/section[2]/div[2]/ol')[0].text.split('\n')

    return clues_across, clues_down


# Function that returns corner numbers and answer letters of puzzle grid as two lists
def get_puzzle_demo(brwsr):
    data = []
    # getting the grid data using css selector
    for index in range(25):
        selector = "#xwd-board > g:nth-child(5) > g:nth-child(" + str(index + 1) + ")"
        if brwsr.find_elements_by_css_selector( selector ):
            data.append(brwsr.find_elements_by_css_selector( selector )[0].text.split('\n'))
        else:
            data.append('')
            
    # we will have two arrays, one for the corner numbers one for the answer letters in the grid
    puzzle_numbers = []
    puzzle_letters = []

    # filling the letters and numbers arrays (mentioned right above)
    for cell in data:
        for i, cell in enumerate(data):
            if len(cell) == 3:
                data[i] = cell[1:]
                circles[i] = 1
                
        for i, cell in enumerate(data):
            if len(cell) == 2 and cell[0] > '9':
                data[i] = cell[1:]
                circles[i] = 1
        
    for cell in data:
        # the cell has a number and letter inside
        if len(cell) == 2: 
            puzzle_numbers.append(cell[0]) # corner number
            puzzle_letters.append(cell[1]) # answer letter
        # the cell has only a letter inside
        else:
            puzzle_numbers.append('') # corner number will be empty string
            puzzle_letters.append(cell[0]) # answer letter, will be empty string if cell is black
            
    return puzzle_numbers, puzzle_letters


# Function that returns the current time (HH:MM:SS) as a formatted string
def get_time_str():
    current_time = str( datetime.now().strftime("%H:%M:%S") )
    # if the first digit is zero, as in 07:30, take it out
    if current_time[0] == '0':
        current_time = current_time[1:]  
    return current_time


# Function that updates bottom text, which shows the time, every 100 milliseconds
def update():
    # format bottom text using the current time:
    bottom_text = date_str + " | " + get_time_str() +  " | " + group_name
        
    puzzle.set_bottom_text( bottom_text )
    root.update()
    root.after(100, update)


# returns a Puzzle, for more information see the class Puzzle
# it should scrape nytimes website and get the puzzle from the given date
def get_puzzle(date):
    # TODO: implement date
    
    # Use chrome driver to get to browser
    googleChromeOptions = webdriver.ChromeOptions()
    # Uncomment the line below if you don't want the chrome browser to pop up
    # if not show_browser:
        # googleChromeOptions.add_argument('--headless')
    chrome_browser = webdriver.Chrome(os.path.abspath(os.curdir) + '/chromedriver', options=googleChromeOptions)
    chrome_browser.get(link)
    sleep(40)
    #element = chrome_browser.find_element_by_xpath('/html/body/div[1]/div/div/div[4]/div/main/div[2]/div/div[2]/div[3]/div/article/button')
    #chrome_browser.execute_script("arguments[0].click();", element)  # print("ACTION: Clicked 'Reveal'")

    
    # (acrross_clues, down_clues) containing lists of strings
    clues = get_clues(chrome_browser)
    
    
    # these are lists of length 25
    corner_numbers, official_solution, black_cells = get_puzzle_data(chrome_browser)
    
    puzzle = Puzzle(clues, corner_numbers, black_cells)
    chrome_browser.close()
    return puzzle, official_solution


# TODO: might move this func to some other file later
def generate_candidates(puzzle, candidate_generators, weights):
    candidates_accross = []
    candidates_down = []
    
    clues = puzzle.clues
    accross_constraints = puzzle.accross_constraints
    down_constraints = puzzle.down_constraints

    
    for i, clue in enumerate(clues[0]):
        length = accross_constraints[i][1]
        candidates = {}
        for i, generator in enumerate(candidate_generators):
            new_candidates = generator.get_candidate_words(clue, length)
            for word in new_candidates.keys():
                if word in candidates:
                    candidates[word] += new_candidates[word] * weights[i]
                else:
                    candidates[word] = new_candidates[word] * weights[i]
        candidates_accross.append(candidates)
            
    for i, clue in enumerate(clues[1]):
        length = down_constraints[i][1]
        candidates = {}
        for i, generator in enumerate(candidate_generators):
            new_candidates = generator.get_candidate_words(clue, length)
            for word in new_candidates.keys():
                if word in candidates:
                    candidates[word] += new_candidates[word] * weights[i]
                else:
                    candidates[word] = new_candidates[word] * weights[i]
        candidates_down.append(candidates)
            
    return candidates_accross, candidates_down


# returns a map where keys=words and values=scores 
# see the class CandidateGenerator for more information
def get_candidates(puzzle):
    # here, use all candidate generators and take the union of their results
    # also, for each candidate score should be the sum of its 
    # scores from all generators
    candidate_generators = []
    weights = []
    # candidate_generators.append(CandidateGenerator(WikiGoogleScraper(), 15))
    # weights.append(1.0)

    # candidate_generators.append(CandidateGenerator(WebsterScraper(), 10))
    # weights.append(1.0)

    candidate_generators.append(CandidateGenerator(Webster_Dic_Scraper(), 10))
    weights.append(1.0)

    # candidate_generators.append(CandidateGenerator(Webster_Dic_Whole_Scraper(), 6))
    # weights.append(1.0)

    candidate_generators.append(CandidateGenerator(Wikipedia_Main_Page_Scrapper(), 30))
    weights.append(1.0)

    candidate_generators.append(CandidateGenerator(Wikipedia_Main_Page_Entire_Clue_Scrapper(), 20))
    weights.append(1.0)

    candidates = generate_candidates(puzzle, candidate_generators, weights)
    return candidates


# returns a pair of lists s.t (across_list, down_list)
# each index in the lists contain a string, this string must consist
# of a single word with no punctuation or empty spaces
def get_solution(puzzle, candidates):
    # print(candidates)
    solution = solve_for(puzzle, candidates)
    return solution


# this just shows the results (both official solution and generated solution)
# on the GUI window using tkinter
def show_results(puzzle, official_solution, solution):
    # gui part
    pass


def main():
    # official_solution should be a 25 long list of chars, 
    # empty string notifies black square
    # for the format of puzzle, see the class Puzzle
    if test_mode:
        # TODO: add dates
        try:
            puzzle = pickle.load(open("puzzle.p", "rb"))
            official_solution = pickle.load(open("offic_soln.p", "rb"))
        except:
            puzzle, official_solution = get_puzzle("TODO: add date")
            pickle.dump(puzzle, open("puzzle.p", "wb"))
            pickle.dump(official_solution, open("offic_soln.p", "wb"))
    else:
        puzzle, official_solution = get_puzzle("TODO: add date")

    # candidates should be a map s.t. key=word, value=score
    # where score is some real value
    if test_mode:
        try:
            candidates = pickle.load(open("save.p", "rb"))
        except:
            candidates = get_candidates(puzzle)
            pickle.dump(candidates, open("save.p", "wb"))
    else:
        candidates = get_candidates(puzzle)
        
        

    # print(candidates[1])

    # solution should be a tuple of lists s.t. (accross_list, down_list)
    # where each index in the lists contain a string?
    solution = get_solution(puzzle, candidates)
    
    # this should show the results on the gui using tkinter
    show_results(puzzle, official_solution, solution)
    
    return solution

    
if __name__ == "__main__":
    selections = main()
    
    # get date and time
    date_str = str(date.today().strftime("%d/%m/%Y"))
    
    # prepare bottom text
    bottom_text = date_str + " | " + get_time_str() + " | " + group_name
    
    # Use chrome driver to get to browser
    googleChromeOptions = webdriver.ChromeOptions()
    
    # Uncomment the line below if you don't want the chrome browser to pop up
    # googleChromeOptions.add_argument('--headless')
    
    chrome_browser = webdriver.Chrome(os.path.abspath(os.curdir) + '/chromedriver', options=googleChromeOptions)

    # Enter the NYT minicrossword webpage
    chrome_browser.get(link)
    #print("ACTION: Opened webpage.")
    
    # Click on "Play without an account"
    # chrome_browser.find_element_by_xpath("//*[@id=\"root\"]/div/div/div[4]/div/main/div[2]/div/div[2]/div[3]/div/article/button").click()
    # element = chrome_browser.find_element_by_xpath("//*[@id=\"root\"]/div/div/div[4]/div/main/div[2]/div/div[2]/div[3]/div/article/button")
    # chrome_browser.execute_script("arguments[0].click();", element)
    sleep(120)

    #print("ACTION: Clicked 'Play without an account'")
    
    # get the clues and grid information, which contains solutions, numbers and specifies the blacked out squares
    across_clues, down_clues = get_clues( chrome_browser )
    #print("ACTION: Revealed the puzzle and acquired the clues.")
    puzzle_numbers, puzzle_letters = get_puzzle_demo( chrome_browser )
    #print("ACTION: Acquired the corner numbers in the grid.")
    #print("ACTION: Acquired the solutions.")

    # print the clues, answer letters and corner numbers of all 25 cells in order
    #print( "\nAcross Clues:\n" + str(across_clues) )
    #print( "\nDown Clues:\n" + str(down_clues) )
    #print( "\nCorner Numbers:\n" + str(puzzle_numbers) )
    #print( "\nSolution Letters:\n" + str(puzzle_letters) )
    
    # print out the puzzle grid for the provided, official solution   
    top_text = "OFFICIAL SOLUTION"
    root = Tk()
    bgcolor = root.cget('bg')
    puzzle = PuzzleFrame(root, 
                         bottom_text, 
                         MARGIN, SIDE, 
                         bgcolor, 
                         puzzle_numbers, puzzle_letters, top_text )
    
    clues = CluesFrame(root, CLUESWIDTH, CLUESHEIGHT, across_clues, down_clues )
    
    # convert the proposed solutions to upper case
    for i in range(2):
        for j in range(5):
            selections[i][j] = selections[i][j].upper()
    
    our_puzzle_letters = []
    
    # let the default guess be a space
    for i in range(25):
        our_puzzle_letters.append(" ")
    
    # show the black boxes in the guessed letters with empty strings    
    for i in range(25):
        if puzzle_letters[i] == "":
            our_puzzle_letters[i] = ""
    
    # set the guessed letters according to the across word selections     
    for i in range(5):
        z = 0
        for j in range(5):
            if puzzle_letters[5*i+j] == "":
                our_puzzle_letters[5*i+j] = ""
                z += 1
            else:
                for k in range( len(selections[0][i]) ):
                    our_puzzle_letters[5*i+z+k] = selections[0][i][k]
                continue
    # set the guessed letters according to the down word selections          
    for i in range(5):
        z = 0
        for j in range(5):
            if puzzle_letters[5*j+i] == "":
                our_puzzle_letters[5*j+i] = ""
                z += 1
            else:
                for k in range( len(selections[1][i]) ):
                    our_puzzle_letters[i+5*z+5*k] = selections[1][i][k]
                continue
    
    # print out the puzzle grid for the proposed solution                 
    top_text = "PROPOSED SOLUTION"
    puzzle2 = PuzzleFrame(root, 
                         "", 
                         MARGIN, SIDE, 
                         bgcolor, 
                         puzzle_numbers, our_puzzle_letters, top_text )
        
    root.geometry("%dx%d" % (WIDTH*3.2, HEIGHT + 30))
    root.after(100, update)
    root.mainloop()