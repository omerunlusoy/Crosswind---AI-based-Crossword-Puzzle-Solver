# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 13:39:24 2021

@author: yigit
"""

import nltk

def nltk_download():
    nltk.download('words')
    nltk.download('punkt')
    nltk.download('wordnet')
    nltk.download('stopwords')
    nltk.download()

if __name__ == "__main__":
    nltk_download()
    