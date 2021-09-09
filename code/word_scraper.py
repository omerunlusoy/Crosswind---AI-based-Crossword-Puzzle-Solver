import os

from selenium.common.exceptions import TimeoutException

from common import show_browser, is_valid, tokenize_text, get_antonyms
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests

from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords

stopwords = stopwords.words("english")

# remove some special characters (e.g. !) from a given clue
def process_clue(clue):
    res = clue
    for c in ['"', "'", "_", ".", ",", "(", ")", "Ç", "!"]:
        res = res.replace(c, "")
    return res


# this class is a wrapper for word scrapers
# each class inheriting it should return a map of words-scores
class WordScraper():
    def __init__(self):
        self.multi_occurence_multiplier = 0.5  # TODO: tune this parameter or remove it?

        # Use chrome driver to get to browser
        googleChromeOptions = webdriver.ChromeOptions()
        # Uncomment the line below if you don't want the chrome browser to pop up
        # if not show_browser:
        # googleChromeOptions.add_argument('--headless')
        self.browser = webdriver.Chrome(os.path.abspath(os.curdir) + '/chromedriver', options=googleChromeOptions)

    def scrape_words(self, clue, grid_length):
        raise NotImplementedError


# a class for scrapping wikipedia google searches
class WikiGoogleScraper(WordScraper):
    def scrape_inside(self, clue, k=1):
        words = {}
        try:
            first_link_xpath = '//*[@id="rso"]/div[2]/div/div/div[1]/a/h3'
            self.browser.find_elements_by_xpath(first_link_xpath)[0].click()
            content_xpath = '//*[@id="content"]'
            lines = self.browser.find_elements_by_xpath(content_xpath)[0].text.split('\n')
            count = len(lines)
            for line in lines:
                cands = line.split()
                for cand in cands:
                    words[cand] = 1.0
        except:
            pass
        return words

    # method that scrapes words given a clue by searching the clue on google,
    # adding site:wikipedia.com to the search bar
    def scrape_words(self, clue, grid_length):
        words = {}

        processed_clue = process_clue(clue)
        print("\nWikipedia Scraping, for the clue: %s" % (processed_clue))
        self.browser.get("https://www.google.com")
        search_bar = self.browser.switch_to.active_element
        search_bar.send_keys("%s site:wikipedia.com" % (process_clue(clue)))
        search_bar.send_keys(Keys.ENTER)

        # TODO: can we make this beforehand?
        self.browser.get(self.browser.current_url + "&lr=lang_en")
        # sleep(0.1)

        if self.browser.current_url == "https://www.google.com/&lr=lang_en":
            return {}
        results = self.browser.find_elements_by_id("rso")

        for result in results:
            result_words = result.text.split()
            count = len(result_words)

            for i, word in enumerate(result_words):
                score = (count - i) / count
                if word in words:
                    # words[word] += score * self.multi_occurence_multiplier
                    pass
                else:
                    words[word] = score

        # possibly scrapes inside
        take_inside_words = False
        if take_inside_words:
            inside_words = self.scrape_inside(clue)
            for word in inside_words:
                if word not in words:
                    words[word] = 0.5

        print("\nThe following words were acquired:")
        print(words)

        return words


# word scrapper for synonyms given a specific clue
class SynonymsScraper(WordScraper):
    def scrape_words(self, clue, grid_length):
        processed_clue = tokenize_text(clue)
        res = {}

        for word in processed_clue:
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

            new_words = synonyms + antonyms
            print(new_words)
            for new_word in res:
                res[new_word] = 0.0

        return res


class WebsterScraper(WordScraper):
    def scrape_words(self, clue, grid_length):
        res = {}

        content_classname = 'mw-list'

        processed_clue = process_clue(clue)
        self.browser.get("https://www.merriam-webster.com/")
        thesaurus_xpath = '//*[@id="mw-search-tabs"]/div[2]/span'
        self.browser.find_elements_by_xpath(thesaurus_xpath)[0].click()
        searchbar_xpath = '//*[@id="s-term"]'

        for word in processed_clue.split():
            if word in stopwords:
                continue
            try:
                WebDriverWait(self.browser, timeout=1).until(
                    ec.visibility_of_element_located((By.XPATH, searchbar_xpath))
                )
            except:
                continue

            searchbar = self.browser.find_elements_by_xpath(searchbar_xpath)[0]
            searchbar.clear()
            searchbar.send_keys(word)
            searchbar.send_keys(Keys.ENTER)

            if "www.merriam-webster" not in self.browser.current_url:
                continue

            elements = self.browser.find_elements_by_class_name(content_classname)
            count = len(elements)

            for i, element in enumerate(elements):
                candidates = element.text.split()
                score = (count - i) / count
                for candidate in candidates:
                    if candidate not in res:
                        res[candidate] = score
                    # else:
                        # res[candidate] += score

        return res


class Webster_Dic_Scraper(WordScraper):
    def scrape_words(self, clue, grid_length):
        res = {}

        content_classname = 'mw-list'

        processed_clue = process_clue(clue)
        self.browser.get("https://www.merriam-webster.com/")
        dictionary_xpath = '//*[@id="mw-search-tabs"]/div[1]/span'
        self.browser.find_elements_by_xpath(dictionary_xpath)[0].click()
        searchbar_xpath = '//*[@id="s-term"]'

        for word in processed_clue.split():
            if word in stopwords:
                continue
            try:
                WebDriverWait(self.browser, timeout=1).until(
                    ec.visibility_of_element_located((By.XPATH, searchbar_xpath))
                )
            except:
                continue

            searchbar = self.browser.find_elements_by_xpath(searchbar_xpath)[0]
            searchbar.clear()
            searchbar.send_keys(word)
            searchbar.send_keys(Keys.ENTER)

            try:
                elements = self.browser.find_elements_by_class_name(content_classname)

                for i, element in enumerate(elements):
                    candidates = element.text.split()
                    count = len(candidates)

                    for ii, candidate in enumerate(candidates):
                        if candidate not in res:
                            score = (count - ii) / count
                            res[candidate] = score
                        # else:
                        # res[candidate] += score

            except TimeoutException:
                continue

        return res


class Webster_Dic_Whole_Scraper(WordScraper):
    def scrape_words(self, clue, grid_length):
        factor = 0.9
        threshold_length = 2
        threshold_score_multiplier = 1.5
        res = {}
        content_classname = 'mw-list'

        processed_clue = process_clue(clue)
        self.browser.get("https://www.merriam-webster.com/")
        dictionary_xpath = '//*[@id="mw-search-tabs"]/div[1]/span'
        # self.browser.find_elements_by_xpath(dictionary_xpath)[0].click()
        searchbar_xpath = '//*[@id="s-term"]'
        clue_length = len(processed_clue.split())

        try:
            WebDriverWait(self.browser, timeout=1).until(
                ec.visibility_of_element_located((By.XPATH, searchbar_xpath))
            )
        except:
            return {}

        searchbar = self.browser.find_elements_by_xpath(searchbar_xpath)[0]
        searchbar.clear()
        searchbar.send_keys(processed_clue)
        searchbar.send_keys(Keys.ENTER)

        try:
            elements = self.browser.find_elements_by_class_name(content_classname)

            for i, element in enumerate(elements):
                candidates = element.text.split()
                count = len(candidates)

                for ii, candidate in enumerate(candidates):
                    if candidate not in res:
                        score = (count - ii) / count
                        res[candidate] = score * factor
                    # else:
                        # res[candidate] += score

        except TimeoutException:
            pass

        return res


class Wikipedia_Main_Page_Scrapper(WordScraper):
    def scrape_words(self, clue, grid_length, word_count=25):
        factor = 1.2

        magic_words = "may refer to:"
        content_texts = {}
        words = process_clue(clue)

        for word in words.split():
            if word in stopwords:
                continue

            self.browser.get('https://en.wikipedia.org/wiki/Main_Page')
            searchbar_xpath = '//*[@id="searchInput"]'

            try:
                WebDriverWait(self.browser, timeout=1).until(
                    ec.visibility_of_element_located((By.XPATH, searchbar_xpath))
                )
            except:
                continue

            searchbar = self.browser.find_elements_by_xpath(searchbar_xpath)[0]
            searchbar.clear()
            searchbar.send_keys(word.lower())
            searchbar.send_keys(Keys.ENTER)
            # click the first thing
            try:
                WebDriverWait(self.browser, timeout=2).until(
                    ec.visibility_of_element_located((By.XPATH, '//*[@id="mw-content-text"]/div[3]/ul/li[1]/div[1]/a/span'))
                )
                element = self.browser.find_element_by_xpath('//*[@id="mw-content-text"]/div[3]/ul/li[1]/div[1]/a/span')
                self.browser.execute_script("arguments[0].click();", element)
            except:
                # try the first suggesting
                first_offering_path = "//*[@id=\"mw-content-text\"]/div[3]/ul/li[1]/div[1]/a"
                second_offering_path = "//*[@id=\"mw-content-text\"]/div[1]/ul[1]/li[1]/a"
                third_offering_path = "//*[@id=\"mw-content-text\"]/div[3]/ul/li[1]/div[1]/a"
                try:
                    element = self.browser.find_element_by_xpath(first_offering_path)
                    self.browser.execute_script("arguments[0].click();", element)
                    element = self.browser.find_element_by_xpath(second_offering_path)
                    self.browser.execute_script("arguments[0].click();", element)
                except:
                    try:
                        element = self.browser.find_element_by_xpath(second_offering_path)
                        self.browser.execute_script("arguments[0].click();", element)
                    except:
                        try:
                            element = self.browser.find_element_by_xpath(third_offering_path)
                            self.browser.execute_script("arguments[0].click();", element)
                        except:
                            url = "https://en.wikipedia.org/wiki/" + word
                            if str(self.browser.current_url).lower() == url.lower():
                                pass
                            else:
                                continue

            # page found
            page = requests.get(self.browser.current_url)

            # scrape webpage
            soup = BeautifulSoup(page.content, 'html.parser')
            list(soup.children)
            count = 0
            for i, e in enumerate(soup.find_all('p')):
                if magic_words in e.get_text():
                    break

                for ii, ee in enumerate(e.get_text().split()):
                    if ee in stopwords or ee.lower() == word.lower() or ee in words:
                        continue
                    if process_clue(ee) in content_texts:
                        score = (word_count - count) / word_count
                        processed_word = process_clue(ee)
                        content_texts[processed_word] += score
                    else:
                        score = (word_count - count) / word_count
                        processed_word = process_clue(ee)
                        content_texts[processed_word] = score * factor
                        count += 1
                    if count == word_count:
                        break
                if count == word_count:
                    break

        return content_texts


class Wikipedia_Main_Page_Entire_Clue_Scrapper(WordScraper):
    def scrape_words(self, clue, grid_length, word_count=25):
        magic_words = "may refer to:"
        content_texts = {}

        word = process_clue(clue)

        self.browser.get('https://en.wikipedia.org/wiki/Main_Page')
        searchbar_xpath = '//*[@id="searchInput"]'

        try:
            WebDriverWait(self.browser, timeout=1).until(
                ec.visibility_of_element_located((By.XPATH, searchbar_xpath))
            )
        except:
            return {}

        searchbar = self.browser.find_elements_by_xpath(searchbar_xpath)[0]
        searchbar.clear()
        searchbar.send_keys(word.lower())
        searchbar.send_keys(Keys.ENTER)
        # click the first thing
        try:
            WebDriverWait(self.browser, timeout=2).until(
                ec.visibility_of_element_located((By.XPATH, '//*[@id="mw-content-text"]/div[3]/ul/li[1]/div[1]/a/span'))
            )
            element = self.browser.find_element_by_xpath('//*[@id="mw-content-text"]/div[3]/ul/li[1]/div[1]/a/span')
            self.browser.execute_script("arguments[0].click();", element)
        except:
            # try the first suggesting
            first_offering_path = "//*[@id=\"mw-content-text\"]/div[3]/ul/li[1]/div[1]/a"
            second_offering_path = "//*[@id=\"mw-content-text\"]/div[1]/ul[1]/li[1]/a"
            third_offering_path = "//*[@id=\"mw-content-text\"]/div[3]/ul/li[1]/div[1]/a"
            try:
                element = self.browser.find_element_by_xpath(first_offering_path)
                self.browser.execute_script("arguments[0].click();", element)
                element = self.browser.find_element_by_xpath(second_offering_path)
                self.browser.execute_script("arguments[0].click();", element)
            except:
                try:
                    element = self.browser.find_element_by_xpath(second_offering_path)
                    self.browser.execute_script("arguments[0].click();", element)
                except:
                    try:
                        element = self.browser.find_element_by_xpath(third_offering_path)
                        self.browser.execute_script("arguments[0].click();", element)
                    except:
                        url = "https://en.wikipedia.org/wiki/" + word
                        if str(self.browser.current_url).lower() == url.lower():
                            pass
                        else:
                            return {}

        # page found
        page = requests.get(self.browser.current_url)

        # scrape webpage
        soup = BeautifulSoup(page.content, 'html.parser')
        list(soup.children)
        count = 0
        for i, e in enumerate(soup.find_all('p')):
            if magic_words in e.get_text():
                break

            for ii, ee in enumerate(e.get_text().split()):
                if ee in stopwords or ee.lower() == word.lower():       # or len(process_clue(ee).lower()) != grid_length
                    continue

                if process_clue(ee) in content_texts:
                    score = (word_count - count) / word_count
                    processed_word = process_clue(ee)
                    content_texts[processed_word] += score
                else:
                    score = (word_count - count) / word_count
                    processed_word = process_clue(ee)
                    content_texts[processed_word] = score
                    count += 1
                if count == word_count:
                    break
            if count == word_count:
                break

        return content_texts
