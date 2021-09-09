# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 12:55:35 2021

@author: yigit
"""

from functools import cmp_to_key
from nltk.corpus import words
import copy
import re
import sys
from nltk.corpus import wordnet as wn

# global variables
all_words = wn.all_lemma_names()
word_scores = None

# This Node class is the main component of our search tree
# it contains the state of a solution which includes:
# current selections, remaining candidates, and depth of node
# constraints are also propagated through the tree for ease of coding,
# however constraints are passed by reference and each node is looking
# at the same constraints, these constraints are never modified
class Node():
    # A simple init function that stores the given values and does
    # reduction based on current selections and constraints
    def __init__(self, candidates, selections, depth, constraints):
        self.candidates = candidates
        self.depth = depth
        self.constraints = constraints
        self.selections = selections
        self.set_selections()
        self.set_constraint_counts()

    # this removes all words from candidates that do not obey the constraints
    # from the current selections
    def reduce(self):
        self.candidates = reduce_by_selections(self.candidates, 
                                               self.selections, 
                                               self.constraints)
        
    # this method is used to find any new implicit selections other than
    # the one given by parent
    # an implicit selection would be a candidate list that has only one member
    # left due to reduction by constraints
    # each such implicit selection is set to the actual selections
    # and reduction is done again
    def set_selections(self):
        self.reduce()
        
        for i, selection in enumerate(self.selections[0]):
            if len(selection) == 0:
                if len(self.candidates[0][i]) == 1:
                    self.selections[0][i] = list(self.candidates[0][i].keys())[0]
                    self.reduce()
                    
        for i, selection in enumerate(self.selections[1]):
            if len(selection) == 0:
                if len(self.candidates[1][i]) == 1:
                    self.selections[1][i] = list(self.candidates[1][i].keys())[0]
                    self.reduce()
    
    # find the number of constraints each candidate will have to obey
    # due to the current selections
    # it is later used to decide which children will be generated
    # see Node.get_children()
    def set_constraint_counts(self):
        self.has_constraints = False
        self.constr_counts = ([0,0,0,0,0],[0,0,0,0,0])
        
        acc_selections = self.selections[0]
        down_selections = self.selections[1]
        
        for constraint in self.constraints:
            acc_idx = constraint[0]
            down_idx = constraint[2]
            
            acc_selection = acc_selections[acc_idx]
            down_selection = down_selections[down_idx]
            
            if len(acc_selection) > 0:
                self.has_constraints = True
                self.constr_counts[1][down_idx] += 1
                
            if len(down_selection) > 0:
                self.has_constraints = True
                self.constr_counts[0][acc_idx] += 1
    
    def is_leaf(self):
        for candidate_map_list in self.candidates:
            for candidate_map in candidate_map_list:
                if len(candidate_map) > 1:
                    return False
                
        return True
    
    def get_hashable(self):
        keys = []

        for candidate in self.candidates:
            for cand_map in candidate:
                keys += cand_map.keys()
                        
        return hash(frozenset(sorted(keys)))
        
    def get_child(self, direction, index, word):
        # direction: 0->accross, 1->down
        candidates = copy.deepcopy(self.candidates)
        candidates[direction][index] = {word: 1.0}
        selections = copy.deepcopy(self.selections)
        selections[direction][index] = word
        depth = self.depth + 1
        
        return Node(candidates, selections, depth, self.constraints)
        
    def get_children(self):
        acc_candidates = self.candidates[0]
        down_candidates = self.candidates[1]
        
        children = []
        
        # if the node is a leaf, return empty list to terminate
        # since it wont have any children
        if self.is_leaf():
            return children
        
        # generate children for all possible accross candidates
        for i, cand_map in enumerate(acc_candidates):
            # if the new selection wont be obeying any constraints
            # we do not need to check that route since it will lead
            # to nodes with all accross selections
            # which is not desired
            # therefore we skip children that does not obey any new
            # constraints
            if self.has_constraints:
                if self.constr_counts[0][i] < 1:
                    continue
                    pass
            
            if len(cand_map) <= 1:
                continue
            
            for word in cand_map.keys():
                children.append(self.get_child(0, i, word))
            
        # generate children for all possible down candidates
        for i, cand_map in enumerate(down_candidates):
            # if the new selection wont be obeying any constraints
            # we do not need to check that route since it will lead
            # to nodes with all down selections
            # which is not desired
            # therefore we skip children that does not obey any new
            # constraints
            if self.has_constraints:
                if self.constr_counts[1][i] < 1:
                    continue
                    pass
            
            if len(cand_map) <= 1:
                continue

            for word in cand_map.keys():
                children.append(self.get_child(1, i, word))
            
        return children

    def get_score(self):
        score = 0.0
        for selection in self.selections:
            for word in selection:
                if len(word) > 0:
                    score += 0
                if word in word_scores:
                    score += word_scores[word]
                    
        return score
        

# This is a function used to sort leafs at the end in order to make 
# the best guess
# leafs are sorted by their scores, for more info see Node.get_score()
def node_compare(node_1, node_2):
    if node_1.get_score() > node_2.get_score():
        return -1
    elif node_1.get_score() == node_2.get_score():
        return 0
    else:
        return 1
    
# given candidates, current selections and all constraints
# remove all candidates that do not obey the constraints of the current selections
def reduce_by_selections(candidates, selections, constraints):
    acc_selections = selections[0]
    down_selections = selections[1]
    
    acc_cands = candidates[0]
    down_cands = candidates[1]
    
    for constraint in constraints:
        acc_idx = constraint[0]
        down_idx = constraint[2]
        
        acc_at = constraint[1]
        down_at = constraint[3]
        
        acc_selection = acc_selections[acc_idx]
        down_selection = down_selections[down_idx]
        
        acc_len = len(acc_selection)
        down_len = len(down_selection)
        
        to_be_removed = []
        
        if acc_len > 0 and down_len > 0:
            continue
        
        if acc_len > 0:
            letter = acc_selection[acc_at]
            for candidate in down_cands[down_idx].keys():
                if candidate[down_at] != letter:
                    to_be_removed.append(candidate)
            for word in to_be_removed:
                down_cands[down_idx].pop(word, None)

        if down_len > 0:
            letter = down_selection[down_at]
            for candidate in acc_cands[acc_idx].keys():
                if candidate[acc_at] != letter:
                    to_be_removed.append(candidate)
            for word in to_be_removed:
                acc_cands[acc_idx].pop(word, None)
                
    return (acc_cands, down_cands)

# helper function of get_letter_counts
# if the word is n characters, returns a list of n dictionaries
# i'th dictionary hold the number of letters seen for the i'th character
# the dictionary has letters as keys, and number of letters seen as values
def get_letter_count_of_word_list(word_list):
    counts = []
    
    if len(word_list) == 0:
        length = -1
    else:
        length = len(word_list[0])
    
    for i in range(length):
        count = {}
        for word in word_list:
            letter = word[i]
            if letter in count:
                count[letter] += 1
            else:
                count[letter] = 1
        counts.append(count)
                
    return counts

# finds the letter counts for all candidate lists
# we will have 10 candidate lists, 5 for accross, 5 for down
# if a candidate list containts words of length n, its letter counts will
# consist of n dictionaries, see get_letter_count_of_word_list(word_list)
# these letter counts are then used for reduction based on constraints
def get_letter_counts(candidates):
    acc_candidates = candidates[0]
    down_candidates = candidates[1]
    
    acc_counts = []
    down_counts = []
    
    for acc_cand_map in acc_candidates:
        word_list = list(acc_cand_map.keys())
        acc_counts.append(get_letter_count_of_word_list(word_list))

    for down_cand_map in down_candidates:
        word_list = list(down_cand_map.keys())
        down_counts.append(get_letter_count_of_word_list(word_list))

    return acc_counts, down_counts
        
def reduce_by_constraints(candidates, letter_counts, constraints):
    # k is the number of constraints a candidate needs to violate in order to
    # be removed
    # setting k higher than 1 increases number of remaining candidates
    # which can help keep the correct answers in the inital list
    # however, it also keeps more of wrong candidates which might lead to
    # wrong answers
    k = 2
    
    acc_candidates = candidates[0]
    down_candidates = candidates[1]
    
    acc_counts = letter_counts[0]
    down_counts = letter_counts[1]
    
    # this flag is used to keep track of changes
    # so that if any candidate was removed, constraint checking is done again
    # if there are no candidates removed in an iteration, then we know
    # there is no more reduction to be done and quit the loop
    flag = True
    
    while (flag):
        # lists of candidates to be removed
        # we need this list because we cannot remove candidates while 
        # iterating over them
        to_be_removed = ([{},{},{},{},{}],[{},{},{},{},{}])
    
        flag = False
        
        for constraint in constraints:
            acc_idx = constraint[0]
            down_idx = constraint[2]
            
            acc_at = constraint[1]
            down_at = constraint[3]
            
            acc_candidate = acc_candidates[acc_idx]
            down_candidate = down_candidates[down_idx]
            
            acc_count = acc_counts[acc_idx]
            down_count = down_counts[down_idx]
            
            for candidate in acc_candidate.keys():
                letter = candidate[acc_at]
                count = 0
                if len(down_count) > 0 and letter in down_count[down_at]:
                    count = down_count[down_at][letter]
                
                if len(down_candidate) > 0 and count == 0:
                    if candidate in to_be_removed[0][acc_idx]:
                        to_be_removed[0][acc_idx][candidate] += 1
                    else:
                        to_be_removed[0][acc_idx][candidate] = 1
                        

            for candidate in down_candidate.keys():
                letter = candidate[down_at]
                count = 0
                if len(acc_count) > 0 and letter in acc_count[acc_at]:
                    count = acc_count[acc_at][letter]
                if  len(acc_candidate) > 0 and count == 0:
                    if candidate in to_be_removed[1][down_idx]:
                        to_be_removed[1][down_idx][candidate] += 1
                    else:
                        to_be_removed[1][down_idx][candidate] = 1

        # remove the candidates that were set to be removed
        for direction in range(2):
            for i in range(5):
                removing = to_be_removed[direction][i]
                for word in removing:
                    if to_be_removed[direction][i][word] >= k:
                        flag = True
                        candidates[direction][i].pop(word, None)
                        for j, letter in enumerate(word):
                            letter_counts[direction][i][j][letter] -= 1
                            
    return candidates, letter_counts

# uses either DFS or BFS method to find all leaves from the given root node
# note that it does not stop at some leaf, instead it generates all leaves
# and returns them all
def get_leafs(root):
    # the method for searching can be selected here
    # BFS lets us see how the stack is growing
    # DFS is going to take less memory and hence be faster
    # however, their time complexities would be the same in this situation
    method = "bfs" # "bfs"
    
    # initialize the stack and list of found leaves
    stack = [root]
    leafs = []
    
    # these dicts are used to store previously seen nodes
    # they are used to prevent expansion of the same node twice
    # if it is acquired through some other path before
    # hence they reduce the total runtime
    seen_dict = {}
    leaf_dict = {}
    
    # while nodes are remaining in the stack
    while len(stack) > 0:
        #print(len(stack))
        
        # pop and expand a node
        node = stack.pop()
        node_hashable = node.get_hashable()
        children = node.get_children()
        
        # add the leaves to leaves list
        if len(children) == 0 and node_hashable not in leaf_dict:
            leaf_dict[node_hashable] = None
            leafs.append(node)
        
        # add the non-leaves to the stack to later be expanded
        for child in children:
            child_hashable = child.get_hashable()
            if child_hashable not in seen_dict:
                seen_dict[child_hashable] = None
                if method == "dfs":
                    stack.append(child)
                elif method == "bfs":
                    stack.insert(0, child)
                else:
                    print("\nSearch method is invalid, exiting:")
                    sys.exit()
                
    return leafs

def get_top_k_helper(cands, k):
    for key in cands.keys():
        cands[key] = word_scores[key]
        
    return dict(sorted(cands.items(), key=lambda item: item[1])[-k:])

def get_top_k(candidates, k):
    for i, cand_map_list in enumerate(candidates):
        for j, cand_map in enumerate(cand_map_list):
            candidates[i][j] = get_top_k_helper(cand_map, k)
            
    return candidates
            

# this is the main function to be called from somewhere else
# it takes in a puzzle which holds clues and constraints
# constraints are a list of tuples that store which entries have crossings
# at which indices
# candidates contains two lists of dictionarites
# each list containts 5 dictionaries and each of these dictionaries holds
# the candidates for the corresponding enrty
# the function then calls all the other helper functions to find a solution
# print it on the console and return it so it can be shown on the gui
def solve_for(puzzle, candidates):
    constraints = puzzle.get_constraints()
    
    # store the word scores globally so they can later be used for ranking
    # possible solutions
    global word_scores
    word_scores = get_word_scores(candidates)
    
    #print_candidates(candidates, puzzle.clues)
    
    # reduce the candidates by constraints
    letter_counts = get_letter_counts(candidates)
    candidates, letter_counts = reduce_by_constraints(candidates, letter_counts, constraints)
    
    candidates = get_top_k(candidates, 30)
    print_candidates(candidates, puzzle.clues)
    # sys.exit()

    print("\nStarting Solving, The candidates we currently have:")
    print()
    # set the initial selections as empty
    # these selections will be held by each node in the search tree
    # and will be making up the state of a node
    selections = [["","","","",""],["","","","",""]]
    
    # construct root node and get the leafs of the tree
    # each leaf will be a possible solution, the best scored leaf will
    # be returned as the proposed solution
    root = Node(candidates, selections, 0, constraints)
    leafs = get_leafs(root)
    leafs = sorted(leafs, key=cmp_to_key(node_compare))
    
    # printing the best 10 leafs and their scores for tracing purposes
    print("\n%d leaves were found: " % (len(leafs)))
    print("Following were the 10 leaves with highest scores: ")
    for i, leaf in enumerate(leafs):
        print(leaf.selections)
        print(leaf.get_score())
        if i > 10:
            break
    
    # print the best guess and return it
    print("\nBest Guess:")
    print(leafs[0].selections)
    # sys.exit()
    return leafs[0].selections
    

########################################################## helper methods
    
def get_word_scores(candidates):
    word_scores = {}
    for cand_map_list in candidates:
        for cand_map in cand_map_list:
            for word in cand_map:
                word_scores[word] = cand_map[word]
                
    return word_scores

def print_candidates(candidates, clues):
    acc_cands = candidates[0]
    down_cands = candidates[1]
    acc_clues = clues[0]
    down_clues = clues[1]
    
    for i, cands in enumerate(acc_cands):
        print()
        print("Clue: %s" % (acc_clues[i]))
        print(cands)

    for i, cands in enumerate(down_cands):
        print()
        print("Clue: %s" % (down_clues[i]))
        print(cands)
        

