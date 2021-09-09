# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 14:37:25 2021

@author: yigit
"""

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
import inflect



p = inflect.engine()

get_antonyms = False

def generate_candidates(clues, candidate_generators, weights):
    # clues will be two lists (accross, down) of strings
    # parse the clues appropriately, pass them through all generators
    # and return the union (scores calculated based on weights?)
    pass

def get_related_words_from_wordnet(word):
    synonyms = []
    antonyms = []
    
    for ss in wn.synsets(word):
        synonyms += ss.lemma_names()
        if get_antonyms:
            for lemma in ss.lemmas():
                ants = [ant.name() for ant in lemma.antonyms()]
                ants = list(dict.fromkeys(ants))
                for ant in ants:
                    for ant_ss in wn.synsets(ant):
                        antonyms += ant_ss.lemma_names()
           
    res = synonyms + antonyms
    res = dict.fromkeys(res)
    return res
    

class CandidateGenerator():
    def __init__(self, word_scraper, k):
        self.k = k
        self.word_scraper = word_scraper
        
        # TODO: make this global maybe?
        self.stopwords = stopwords.words("english")
    
    def plural_to_singular(self, words):
        # TODO: plural nouns singular and add them to the map
        # copy their scores from parent?
        # apply penalty?
        
        # https://pypi.org/project/inflect/
        return words
    
    def singular_to_plural(self, words):
        plurals = {}
        
        for word in words.keys():
            plural = p.plural(word)
            if plural not in plurals:
                plurals[plural] = words[word] * 0.3
                
        for plural in plurals.keys():
            if plural not in words:
                words[plural] = plurals[plural]
                
        return words 
    
    
    def normalize_words(self, words):
        # TODO: get rid of punctuation, make them all lower case
        new_words = {}
        word_list = words.keys()
        for word in word_list:
            tokens = word_tokenize(word)
            tokens = [t.lower() for t in tokens if t.isalpha()]
            for token in tokens:
                if token not in self.stopwords and token.isascii():
                    new_words[token] = words[word]
                    
        return new_words
    
    # TODO: add stemmer?
    
    def add_synsets(self, words):
        syns_list = {}
        for word in words:
            syns = get_related_words_from_wordnet(word)
            syns = self.normalize_words(syns)
            for syn in syns.keys():
                if syn not in syns_list:
                    syns_list[syn] = words[word] * 0.3
            
        for syn in syns_list.keys():
            if syn not in words:
                words[syn] = syns_list[syn]
        return words
    
    def remove_invalid_lengths(self, words, length):
        # TODO: shoul be obvious
        new_words = {}
        word_list = words.keys()
        for word in word_list:
            if len(word) == length:
                new_words[word] = words[word]
                
        return new_words
    
    
    def get_candidate_words(self, clue, length):
        words = self.word_scraper.scrape_words(clue, length)
        
        words = self.normalize_words(words)
        print("After removing stopwords and punctuation:")
        print(words)
        # words = self.add_synsets(words)
        words = self.singular_to_plural(words)
        words = self.plural_to_singular(words)
        words = self.remove_invalid_lengths(words, length)
        
        
        words_to_remove = ["eksik", "one", "www", "web", "bir", "arama", 
                           "var", "yap", "pdf", "net", "cum", "yok", "kek",
                           "https", "wiki"]
        for word in words_to_remove:
            words.pop(word, None)
        
        print("Selected the appropriate length (%d) words:" % (length))
        print(words)
        
        
        result = dict(list(reversed(sorted(words.items(), key=lambda item: item[1])))[:self.k])
        print("First %d words selected (sorted by score):" % (self.k))
        print(result)

        return result
    
    
def test_synsets():
    word = "this"
    
    print(get_related_words_from_wordnet(word))
            


if __name__ == "__main__":
    pass
    
    
    
    