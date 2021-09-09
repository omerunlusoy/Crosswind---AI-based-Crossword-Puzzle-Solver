# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 10:39:31 2021

@author: yigit
"""

from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

all_words = dict.fromkeys(wn.all_lemma_names())
eng_stopwords = stopwords.words("english")

def is_valid(word):
    return word in all_words

def tokenize_text(text):
    new_words = {}
    word_list = text.split()
    for word in word_list:
        tokens = word_tokenize(word)
        tokens = [t.lower() for t in tokens if t.isalpha()]
        for token in tokens:
            if token not in eng_stopwords and token.isascii():
                new_words[token] = None
                
    return list(new_words)

# this file should hold the parameters used more than one file

show_browser = True
test_mode = True
get_antonyms = False

