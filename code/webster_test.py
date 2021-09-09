# -*- coding: utf-8 -*-
"""
Created on Tue May  4 11:42:10 2021

@author: yigit
"""

from selenium import webdriver
from common import show_browser
from selenium.webdriver.common.keys import Keys


word = "dummy"

# Use chrome driver to get to browser
googleChromeOptions = webdriver.ChromeOptions()
# Uncomment the line below if you don't want the chrome browser to pop up
if not show_browser:
    googleChromeOptions.add_argument('--headless')
browser = webdriver.Chrome(options = googleChromeOptions)

browser.get("https://www.merriam-webster.com/")
thesaurus_xpath = '//*[@id="mw-search-tabs"]/div[2]/span'
browser.find_elements_by_xpath(thesaurus_xpath)[0].click()
searchbar_xpath = '//*[@id="s-term"]'
browser.find_elements_by_xpath(searchbar_xpath)[0].send_keys(word)
browser.find_elements_by_xpath(searchbar_xpath)[0].send_keys(Keys.ENTER)


content_xpath = 'mw-list'
elements = browser.find_elements_by_class_name(content_xpath)


