# Initial Config
import driving_theory

# Functions
def evaluate_per_page(driver):
    """
    Evaluates an answer to a question given some multiple choices per page in the following
    fashion:

        - After the driving test has been started, it evaluates what the question is.
        - It identifies what are the choices of answers it has.
        - It makes a dictionary of those choices along with their ids on the page.
        - It obtains the answer from Google by looking at the first paragraph it sees.
        - It scores each answer based on the answer from Google and evaluates what it thinks
        will be the best answer to the question.
        - It clicks on the answer; using the answer-id from the choices_dict
    Parameters
    ----------
    driver: the selenium driver used to open the webpage and start the test.

    Returns
    -------
    A page evaluate with an answer chosen.

    """
    # Identify the question
    question_class_name = "govuk-fieldset__heading"
    question = driving_theory.StartTest().identify_question(
        driver=driver, question_class_name=question_class_name
    )

    # Identify the choices
    choice_class_name = "govuk-radios"
    choices = driving_theory.StartTest().identify_choices(
        driver=driver, choice_class_name=choice_class_name
    )

    # Make a choices dict
    choices_dict = driving_theory.StartTest().make_choices_dict(choices=choices)

    # Obtain the answer from Google
    # If the question is pictorial, obtain the answer using the ImageDetection
    # & ImageSearch classes
    image_xpath = '//*[@id="main-content"]/div[1]/div/div[3]/div[1]/div[1]/div/div[2]/fieldset/div/div[1]/p/img'
    image_detection, image_body = driving_theory.ImageDetection().detect_image(
        driver=driver, image_xpath=image_xpath
    )
    if image_detection:
        # If there is an image detected, obtain its URL
        image_url = driving_theory.ImageDetection().get_image_url(image_body=image_body)

        # Make a new tab
        driving_theory.ImageSearch().new_tab(driver=driver)

        # Switch control to the new tab opened
        driving_theory.ImageSearch().switch_tab(driver=driver)

        # Open Google Image Search in the new tab
        driver.get("https://www.google.com/imghp?hl=EN")

        # Accept the cookies
        accept_button_xpath = '//*[@id="L2AGLb"]'
        driving_theory.ImageSearch().accept_google_search_cookies(
            driver=driver, accept_button_xpath=accept_button_xpath
        )

        # Search for the image and obtain an answer
        cam_button_xpath = '//*[@id="sbtc"]/div/div[3]/div[2]/span'
        url_tab_xpath = '//*[@id="dRSWfb"]/div/div'
        image_url_id = "Ycyxxc"
        search_button_id = "RZJ9Ub"
        first_answer_xpath = '//*[@id="topstuff"]/div/div[2]/a'
        answer = driving_theory.ImageSearch().image_search(
            driver=driver,
            image_url_path=image_url,
            cam_button_xpath=cam_button_xpath,
            url_tab_xpath=url_tab_xpath,
            image_url_id=image_url_id,
            search_button_id=search_button_id,
            first_answer_xpath=first_answer_xpath,
        )

        # Switch back control to the original tab
        driving_theory.ImageSearch().switch_to_original_tab(driver=driver)
    else:
        # If no image is detected, then use the AnswerSearch class instead
        try:
            # Try to obtain the correct answer
            answer = driving_theory.AnswerSearch().answer_search(question=question)
        except:
            # If an answer cannot be obtained, choose a random one
            answer = driving_theory.CorrectAnswer().random_answer(choices_dict=choices_dict)

    # Obtain the correct answer amongst the choices
    correct_answer = driving_theory.CorrectAnswer().obtain_correct_answer(
        question=question, answer=answer, choices_dict=choices_dict
    )

    # Click on the answer
    driving_theory.StartTest().click_answer(
        driver=driver, correct_answer=correct_answer, choices_dict=choices_dict
    )


def evaluate_all_pages(driver):
    """
    Evaluates all the pages in the driving test using the evaluate_per_page func.
    Uses recursion to keep on evaluating pages until there is none left to evaluate.

    Parameters
    ----------
    driver: the selenium driver used to open the webpage and start the test.

    Returns
    -------
    All the pages evaluated in the driving theory test.

    """
    # Evaluate the page
    evaluate_per_page(driver)

    # Go onto next page
    next_page_button_id = "btn-next"
    driving_theory.StartTest().next_page(
        driver=driver, next_page_button_id=next_page_button_id
    )

    evaluate_all_pages(driver)


def complete_theory_test():
    """
    Completes the driving theory test from start to finish using the functions: evaluate_per_page &
    evaluate_all_pages.

    Returns
    -------
    Hopefully a passmark for the driving theory test.

    """
    # Initial Config
    url = "https://www.safedrivingforlife.info/free-practice-tests/practice-theory-test-for-car-drivers-1-of-2/"
    start_xpath = '//*[@id="main-content"]/div[1]/div/div[2]/button'

    # Start the test
    driver = driving_theory.StartTest().open_webpage(url=url, start_xpath=start_xpath)

    evaluate_all_pages(driver)


def main():
    """
    The main function.

    """
    complete_theory_test()


# Execution
if __name__ == "__main__":
    main()
