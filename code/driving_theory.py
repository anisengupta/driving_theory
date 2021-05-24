# Initial Config
import spacy

spacy.load("en_core_web_sm")
from spacy.lang.en import English

parser = English()

import nltk

nltk.download("wordnet")
from nltk.corpus import wordnet as wn

from nltk.stem.wordnet import WordNetLemmatizer

import os
import unicodedata

import requests
import urllib
import pandas as pd
from requests_html import HTML
from requests_html import HTMLSession

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# Classes
class AnswerSearch:
    """
    Class searches for the answer to the multiple-choice question by utilising
    Google and retrieving an answer in the form of the first description available.

    """

    def __init__(self):
        pass

    def get_source(self, url: str):
        """
        Creates a HTML session by retrieving a response from the URL.
        If the retrieval is successful, a response 200 will be returned.

        Parameters
        ----------
        url: str, the URL param.

        Returns
        -------
        A response with a relevant code.

        """
        try:
            session = HTMLSession()
            response = session.get(url)
            return response

        except requests.exceptions.RequestException as e:
            print(e)

    def get_results(self, query: str):
        """
        Uses the func get_source to return the results of the google search
        based on the query param.
        Parameters
        ----------
        query: str, the query to be searched.

        Returns
        -------
        A response with a relevant code. If it is 200, then the retrieval
        is successful.

        """

        query = urllib.parse.quote_plus(query)
        response = AnswerSearch().get_source(
            "https://www.google.co.uk/search?q=" + query
        )

        return response

    def answer_search(self, question: str) -> str:
        """
        Searches for an answer to a question based on a Google search.

        Parameters
        ----------
        question: str, the initial question input.

        Returns
        -------
        A string with the answer to the question.

        """
        response = AnswerSearch().get_results(question)
        css_identifier_text = ".hgKElc"
        results = response.html.find(css_identifier_text)

        return results[0].find(css_identifier_text, first=True).text


class ImageDetection:
    """
    Class attempts to detect an image in a multiple choice question.

    """

    def __init__(self):
        pass

    def detect_image(self, driver, image_xpath: str):
        """
        Assesses whether an image is present on the given xpath.

        Parameters
        ----------
        driver: the selenium driver used to open the webpage and start the test.
        image_xpath: str, the xpath of the image to look for.

        Returns
        -------
        A bool and the body of the image, if present on the page.

        """
        outcome = False
        image_body = ""
        # Determine if the image body is present on the page
        try:
            image_body = driver.find_element_by_xpath(image_xpath)
            outcome = True
        except Exception as e:
            print(e)

        return outcome, image_body

    def get_image_url(self, image_body) -> str:
        """
        Returns the url of the image if present on the page. Image body is created
        from the func detect_image.

        Parameters
        ----------
        image_body: the selenium webdriver WebElement, generated from the detect_image func.

        Returns
        -------
        The url of the image.

        """
        return image_body.get_attribute("src")


class ImageSearch:
    """
    In the event that a pictorial question is asked ('What is this sign?'); class attempts to
    search the image using its URL and a different tab to the one already being used
    for the test.

    """

    def __init__(self):
        pass

    def new_tab(self, driver):
        """
        Opens a new tab on an already existing webdriver.
        Parameters
        ----------
        driver: the selenium driver used to open the webpage and start the test.

        Returns
        -------
        A new tab being opened on the webpage opened.

        """
        driver.execute_script("window.open('','_blank');")

    def switch_tab(self, driver):
        """
        Switches the tab of the driver.

        Parameters
        ----------
        driver: the selenium driver used to open the webpage and start the test.

        Returns
        -------
        The control being passed to the tab just opened using the new_tab func.

        """
        window_handles = driver.window_handles

        driver.switch_to_window(window_handles[-1])

    def switch_to_original_tab(self, driver):
        """
        Switches back control to the original tab of the driver.

        Parameters
        ----------
        driver: the selenium driver used to open the webpage and start the test.

        Returns
        -------
        Control being switched over to the original tab to carry on the test.

        """
        window_handles = driver.window_handles

        driver.switch_to_window(window_handles[0])

    def accept_google_search_cookies(self, driver, accept_button_xpath: str):
        """
        Accepts the cookies on Google search.

        Parameters
        ----------
        driver: the selenium driver used to open the webpage and start the test.
        accept_button_xpath: str, the xpath of the accept button.

        Returns
        -------
        Accepts the cookies on Google search and allows you to continue
        with the search.

        """

        buddy = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, accept_button_xpath))
        )
        buddy.click()

    def image_search(
        self,
        driver,
        image_url_path: str,
        cam_button_xpath: str,
        url_tab_xpath: str,
        image_url_id: str,
        search_button_id: str,
        first_answer_xpath: str,
    ) -> str:
        """
        Conducts an image search on Google images based on the image_url_path param.
        Once searches are made, it returns the first answer.

        Parameters
        ----------
        driver: the selenium driver used to open the webpage and start the test.
        image_url_path: str, the url of the image to be searched.
        cam_button_xpath: str, the xpath of the camera icon button.
        url_tab_xpath: str, the xpath of the url tab.
        image_url_id: str, the id of the image url input.
        search_button_id: str, the id of the search button to be clicked.
        first_answer_xpath: str, the xpath of the first answer.

        Returns
        -------
        An answer to what the image could be according to Google image search.

        """
        # Open Google Image search in the other tab
        driver.get("https://www.google.com/imghp?hl=EN")

        # Find cam button
        cam_button = driver.find_element_by_xpath(cam_button_xpath)
        cam_button.click()

        # Find image url tab
        url_tab = driver.find_element_by_xpath(url_tab_xpath)
        url_tab.click()

        # Set the image url
        image_url = driver.find_element_by_id(image_url_id)
        image_url.clear()
        image_url.send_keys(image_url_path)

        # Click on the search button
        submit_button = driver.find_element_by_id(search_button_id)
        submit_button.click()

        # Identify the answer
        answer = driver.find_element_by_xpath(first_answer_xpath)

        return answer.text


class CorrectAnswer:
    """
    Class tries to determine the correct answer to the question presented. There are usually four answers
    in multiple choice and the correct answer is tried to be determined from the initial question.

    """

    def __init__(self):
        pass

    def tokenize(self, text: str) -> list:
        """
        Splits up the text body into smaller list in a list.
        Parameters
        ----------
        text: str, the initial body of text supplied.

        Returns
        -------
        A list of the text split up.

        """
        lda_tokens = []
        tokens = parser(text)
        for token in tokens:
            if token.orth_.isspace():
                continue
            elif token.like_url:
                lda_tokens.append("URL")
            elif token.orth_.startswith("@"):
                lda_tokens.append("SCREEN_NAME")
            else:
                lda_tokens.append(token.lower_)
        return lda_tokens

    def get_lemma(self, word: str) -> str:
        """
        Finds the meanings of words, synonyms and antonyms using the NLTK's wordnet.

        Parameters
        ----------
        word: str, the initial string input.

        Returns
        -------
        A string with the meaning of the word returned.

        """
        lemma = wn.morphy(word)
        if lemma is None:
            return word
        else:
            return lemma

    def get_lemma2(self, word):
        """
        Finds the root of the word input.

        Parameters
        ----------
        word: str, the initial string input.

        Returns
        -------
        A string returning the root of the word input.

        """
        return WordNetLemmatizer().lemmatize(word)

    def prepare_text_for_lda(self, text) -> list:
        """
        Takes the input text and returns the topics in a list.

        Parameters
        ----------
        text: str, the initial text input.

        Returns
        -------
        A list of words that are the topics of the initial text input.

        """
        nltk.download("stopwords")
        en_stop = set(nltk.corpus.stopwords.words("english"))

        tokens = CorrectAnswer.tokenize(self, text)
        tokens = [token for token in tokens if len(token) > 4]
        tokens = [token for token in tokens if token not in en_stop]
        tokens = [CorrectAnswer.get_lemma(self, token) for token in tokens]
        return tokens

    def unicode_to_ascii(self, string: str) -> str:
        """
        Converts a text input to its unicode equivalent.

        Parameters
        ----------
        string: str, the string input.

        Returns
        -------
        The unicode equivalent of the string input.

        """
        string = unicodedata.normalize("NFD", string).encode("ascii", "ignore")
        return string

    def get_n_grams(self, text: list, n: int) -> list:
        """
        Returns the n-grams of a list based on the n param input.

        If the input list is ['brakes', 'warning', 'light', 'stays'], then the n-grams
        calculation will be [['brakes', 'warning'], ['warning', 'light'], ['light', 'stays']]
        if the n param is 2.

        Parameters
        ----------
        text: list, the initial input list.
        n: int, the initial integer to create the n-grams.

        Returns
        -------
        A list of n-grams.

        """
        # Make an empty list
        grams = []

        # For each index in the text list param - (n + 1)
        for i in range(len(text) - n + 1):
            grams.append(
                # For each element in text within the range ending i + n
                # append to grams
                [text[j] for j in range(i, i + n)]
            )

        return grams

    def get_grams(self, question: str) -> dict:
        """
        Makes a dict of the unigrams, bigrams and the full question, uses the func
        get_n_grams.

        Parameters
        ----------
        question: str, the initial question being asked.

        Returns
        -------
        A dict of the unigrams, bigrams and the full question. From these we can create
        a scoring system to determine the correct answer to a given question.

        """
        words = question.split()
        words = [word.lower() for word in words]

        unigrams = CorrectAnswer().prepare_text_for_lda(text=question)

        bigrams = []

        if len(words) > 2:
            raw_bigrams = CorrectAnswer().get_n_grams(words, 2)

            bigrams = []
            for bigram in raw_bigrams:
                bigrams.append(" ".join(bigram))

        grams = {
            "unigrams": unigrams,
            "bigrams": bigrams,
            "complete": CorrectAnswer().unicode_to_ascii(question),
        }

        return grams

    def negative_question(self, question: str) -> bool:
        """
        Determines if a question is negative, eg Which of these is NOT true?

        Parameters
        ----------
        question: str, the initial question string input.

        Returns
        -------
        A bool to determine whether the question input param.

        """
        negative_patterns = ["NOT"]

        for negative_pattern in negative_patterns:
            if negative_pattern in question:
                return True

        return False

    def remove_question_from_answer(self, text: str, question: str) -> str:
        """
        Removes the initial question from the answer provided. Note that is assumed that the
        answer input (text param) is scraped from a search engine.

        Parameters
        ----------
        text: str, the initial answer input.
        question: str, the question input.

        Returns
        -------
        A string with the question removed. If the answer does not contain the original
        question, then the initial text input is just returned.

        """
        # Replace instances of single and double spaces
        return text.replace(question, "").replace("\n     \n    ", "").replace("\n", "")

    def base_answer_method(self, choice: str, answer: str, question: str) -> int:
        """
        The base method to choosing an answer to a question. Method naively makes a count
        of how many times the choice appears in the answer.

        Parameters
        ----------
        choice: str, the answer choice.
        answer: str, the answer, scraped from the web.
        question: str, the question input param.

        Returns
        -------
        A score based on how many times the choice appears on the answer.

        """
        # Process the choice
        choice_processed = CorrectAnswer().prepare_text_for_lda(text=choice)

        # Process the answer
        answer = CorrectAnswer().remove_question_from_answer(
            text=answer, question=question
        )
        answer_processed = CorrectAnswer().prepare_text_for_lda(text=answer)

        score = 0
        for processed_choice in choice_processed:
            print(processed_choice)
            score += answer_processed.count(processed_choice)

        return score

    def gram_answer_method(self, choice: str, answer: str, question: str) -> int:
        """
        Another answering a multiple choice method that is slightly more complex than the
        base method.

        Parameters
        ----------
        choice: str, the answer choice.
        answer: str, the answer, scraped from the web.
        question: str, the question input param.

        Returns
        -------
        A score based on the number of n-grams from the choice that appears in the question.

        """
        # Process the answer
        answer = CorrectAnswer().remove_question_from_answer(
            text=answer, question=question
        )
        answer_processed = CorrectAnswer().prepare_text_for_lda(text=answer)

        score = 0

        grams = CorrectAnswer().get_grams(choice)

        mult = {"unigrams": 1, "bigrams": 3, "complete": 10}

        for gram_type in grams:
            gram_type_score = 0

            for gram in grams[gram_type]:
                gram_type_score += answer_processed.count(gram)

            score += mult[gram_type] * gram_type_score

        return score

    def obtain_correct_answer(
        self, question: str, answer: str, choices_dict: dict
    ) -> str:
        """
        Attempts to obtain the correct answer from the multiple choice values and
        questions presented. Note that you also have to pass an answer to it.

        Parameters
        ----------
        question: str, the question input param.
        answer: str, the answer, scraped from the web.
        choices_dict: dict, makes a dictionary of the multiple choices per page.
        Obtained from the func make_choices_dict in the StartTest class.

        Returns
        -------
        A string with (hopefully) should be the right answer to the question.

        """
        # Make a list of choices from the choices_dict
        choices = list(choices_dict.keys())

        # For each choice, evaluate its score
        scores = []

        for choice in choices:
            score = CorrectAnswer().gram_answer_method(
                choice=choice, answer=answer, question=question
            )

            scores.append(score)

        # Make a dictionary of the choices and their scores
        score_dict = dict(zip(choices, scores))

        # Obtain the correct answer from the highest score given
        correct_answer = ""

        for choice, score in score_dict.items():
            if score == max(list(score_dict.values())):
                correct_answer = choice

        return correct_answer


class StartTest:
    """
    Class makes use of the selenium module and starts the driving theory test.
    Note that this is assuming that the correct webdriver has already been downloaded
    (for the relevant operating software) and initialised.

    """

    def __init__(self):
        pass

    def open_webpage(self, url: str, start_xpath: str):
        """
        Opens the webpage and starts the test.

        Parameters
        ----------
        url: str, the initial starting URL.
        start_xpath: the xpath of the start button.

        Returns
        -------
        A chrome browser navigated to the website and the test started.

        """
        # Initiate the Chrome driver
        driver = webdriver.Chrome("/usr/local/bin/chromedriver")

        # Initiate the url to be accessed
        driver.get(url)

        # Click the start button
        driver.find_element_by_xpath(start_xpath).click()

        return driver

    def identify_question(self, driver, question_class_name: str) -> str:
        """
        Identifies the question on the page the url is accessed and the test is started.

        Parameters
        ----------
        driver: the selenium used to open the webpage and start the test.
        question_class_name: str, the class name of the question.

        Returns
        -------
        A string with the question being asked.

        """
        # Wait 10 seconds until the page loads
        buddy = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, question_class_name))
        )

        # Identify the question
        question = driver.find_element_by_class_name(question_class_name)

        return question.text

    def identify_choices(self, driver, choice_class_name: str):
        """
        Identifies the multiple choices per page.

        Parameters
        ----------
        driver: the selenium driver used to open the webpage and start the test.
        choice_class_name: str, the name of the overall multiple choices per page.

        Returns
        -------
        A selenium choices object.

        """
        # Wait 10 seconds until the page loads
        buddy = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, choice_class_name))
        )

        # Identify the answers
        choices = driver.find_element_by_class_name(choice_class_name)

        return choices

    def make_choices_dict(self, choices) -> dict:
        """
        Makes a dictionary of the multiple choices per page.

        Parameters
        ----------
        choices: the selenium like object, created with the identify choices func.

        Returns
        -------
        A dict of the choices as keys and a value assigned to them.

        """
        # Make choices list
        choices_list = choices.text.split("\n")

        # Make a keys list
        keys = ["questions-0", "questions-1", "questions-2", "questions-3"]

        return dict(zip(choices_list, keys))

    def click_answer(self, driver, correct_answer: str, choices_dict: dict):
        """
        Obtains the id of the correct answer and proceeds to click on it.

        Parameters
        ----------
        driver: the selenium driver used to open the webpage and start the test.
        correct_answer: str, the answer obtained from the func obtain_correct_answer
        in the CorrectAnswer class.
        choices_dict: a dict of the choices as keys and a value assigned to them. Made from
        the func make_choices_dict in the StartTest class.

        Returns
        -------
        The answer selected on the page.

        """
        # Find the id of the correct_answer
        correct_answer_id = choices_dict.get(correct_answer)

        # Make the driver click on the correct answer
        driver.find_element_by_id(correct_answer_id).click()

    def next_page(self, driver, next_page_button_id: str):
        """
        Goes onto the next page to evaluate the choices to the question given.

        Parameters
        ----------
        driver: the selenium driver used to open the webpage and start the test.
        next_page_button_id: str, the id of the next-page button on the page.

        Returns
        -------
        The function goes to the next page

        """
        # Click the next page button
        driver.find_element_by_id(next_page_button_id).click()

    def end_test(self, driver, end_button_id: str):
        """
        Ends the test by clicking on the 'End test' button.

        Parameters
        ----------
        driver: the selenium driver used to open the webpage and start the test.
        end_button_id: str, the id of the end-test button on the page.

        Returns
        -------
        The ending of the driving theory test.

        """
        driver.find_element_by_class_name(end_button_id).click()
