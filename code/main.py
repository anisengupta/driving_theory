# Initial Config
import driving_theory
from IPython.display import clear_output
import logging

# Functions
def evaluate_per_page(driver, highway_code_image_dict: dict):
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
    highway_code_image_dict: dict, an image bank of dicts obtained from
    the Highway Code website.

    Returns
    -------
    A page evaluate with an answer chosen.

    """
    # Identify the question
    logging.info("Identifying the questions")
    question_class_name = "govuk-fieldset__heading"
    question = driving_theory.StartTest().identify_question(
        driver=driver, question_class_name=question_class_name, wait_time=10
    )
    logging.info(question)

    # Identify the choices
    logging.info("Identifying the choices")
    choice_class_name = "govuk-radios"
    choices = driving_theory.StartTest().identify_choices(
        driver=driver, choice_class_name=choice_class_name, wait_time=10
    )

    # Make a choices dict
    logging.info("Making a choices dictionary")
    choices_dict = driving_theory.StartTest().make_choices_dict(choices=choices)

    # Obtain the answer from Google
    # If the question is pictorial, obtain the answer using the ImageDetection
    # & ImageSearch classes
    logging.info("Detecting whether there is an image on the page")
    image_xpath = '//*[@id="main-content"]/div[1]/div/div[3]/div[1]/div[1]/div/div[2]/fieldset/div/div[1]/p/img'
    image_detection, image_body = driving_theory.ImageDetection().detect_image_question(
        driver=driver, image_xpath=image_xpath
    )
    if image_detection:
        logging.info("Image on page detected")
        # If there is an image detected, obtain its URL
        logging.info("Obtaining its URL")
        image_url = driving_theory.ImageDetection().get_image_url(image_body=image_body)

        # Lets see if we can use the ImageComparison class to obtain a caption
        # Obtain an initial answer
        logging.info("Obtaining an answer for the image")
        threshold = 10
        answer = driving_theory.ImageComparison().get_sign_meaning(
            highway_code_image_dict=highway_code_image_dict,
            test_img_url=image_url,
            threshold=threshold,
        )
        logging.info(answer)

        # If the initial method doesnt find an answer, use the ImageSearch class
        if answer == "No caption found":
            logging.info("No caption found for the image, opening a new tab")
            # Make a new tab
            driving_theory.ImageSearch().new_tab(driver=driver)

            # Switch control to the new tab opened
            logging.info("Switching control to new tab")
            driving_theory.ImageSearch().switch_tab(driver=driver)

            # Open Google Image Search in the new tab
            logging.info("Performing Google search")
            driver.get("https://www.google.com/imghp?hl=EN")

            # Accept the cookies
            try:
                logging.info("Accepting the cookies")
                accept_button_xpath = '//*[@id="L2AGLb"]'
                driving_theory.ImageSearch().accept_google_search_cookies(
                    driver=driver, accept_button_xpath=accept_button_xpath, wait_time=1
                )
            except:
                logging.info(
                    "Looks like the cookies have already been accepted, continuing"
                )
                # Note that if an exception is returned, it means that
                # cookies are already accepted
                pass

            # Search for the image and obtain an answer
            logging.info("Searching for the answer to the image")
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
            logging.info(answer)

            # Close the tab opened
            logging.info("Closing the tab")
            driving_theory.ImageSearch().close_tab(driver=driver)

            # Switch back control to the original tab
            logging.info("Giving back control to the original tab")
            driving_theory.ImageSearch().switch_to_original_tab(driver=driver)
        else:
            logging.info("Looks like the initial image answering method worked")
            # If the initial method using the ImageComparison class worked,
            # just use that as the answer
            answer = answer
            logging.info(answer)
    else:
        logging.info("Evaluating the choices_dict created")
        choices_dict_eval = driving_theory.StartTest().evaluate_choices_dict(
            choices_dict=choices_dict
        )
        logging.info(choices_dict_eval)

        if choices_dict_eval:
            logging.info("Looks like there are empty strings in the choices_dict")
            logging.info(
                "This means that the answers do not contain text, they contain images"
            )
            # If the choices_dict_eval is True - it contains empty strings
            image_answers_class_name = "choice-image"
            logging.info("Obtaining the image urls of the answers")
            image_urls = driving_theory.ImageDetection().detect_image_answers(
                driver=driver, image_answers_class_name=image_answers_class_name
            )

            # Identify whether the question being asked is a shape one
            logging.info("Identifying whether the question being asked is a shape one")
            shape_question = driving_theory.StartTest().identify_shape_question(
                question=question
            )

            if shape_question:
                logging.info("Looks like a shape question is detected")
                shapes = []

                logging.info("Obtaining the shapes for the images")
                for image_url in image_urls:
                    shape = driving_theory.ImageComparison().detect_shape(
                        image_url=image_url
                    )
                    shapes.append(shape)

                logging.info("Updating the choices_dict with the images shapes")
                choices_dict = driving_theory.ImageAnswers().update_choices_dict(
                    captions=shapes
                )
            else:
                logging.info(
                    "Attempting to obtain an answer, a captions_dict and the answers_outcome"
                )
                (
                    answer,
                    captions_dict,
                    answer_outcome,
                ) = driving_theory.ImageAnswers().image_answer(
                    image_urls=image_urls,
                    highway_code_image_dict=highway_code_image_dict,
                    question=question,
                )
                logging.info(answer_outcome)
                logging.info(answer)

                # Update the choices_dict accordingly
                if answer_outcome == "Answer obtained":
                    logging.info("Looks like an answer was obtained")
                    # If an answer is obtained then update the choices_dict
                    logging.info("Obtaining a list of captions")
                    captions = list(captions_dict.keys())
                    logging.info(captions)

                    logging.info("Updating the choices_dict")
                    choices_dict = driving_theory.ImageAnswers().update_choices_dict(
                        captions=captions
                    )
                else:
                    logging.info(
                        "An answer was not obtained, keeping the choices_dict the same"
                    )
                    # If no answer is obtained then do not change the choices_dict
                    choices_dict = choices_dict

        # If no image is detected, then use the AnswerSearch class instead
        logging.info("Looks like there are no images detected")
        try:
            # Try to obtain the correct answer
            logging.info("Attempting to obtain a correct answer")
            answer = driving_theory.AnswerSearch().answer_search(question=question)
        except:
            logging.info("It looks an answer cannot be obtained, choosing a random one")
            # If an answer cannot be obtained, choose a random one
            answer = driving_theory.CorrectAnswer().random_answer(
                choices_dict=choices_dict
            )

    # Obtain the correct answer amongst the choices
    logging.info("Attempting to obtain a correct answer amongst the choices")
    correct_answer = driving_theory.CorrectAnswer().obtain_correct_answer(
        question=question, answer=answer, choices_dict=choices_dict
    )
    logging.info(correct_answer)

    # Click on the answer
    logging.info("Clicking on the answer")
    driving_theory.StartTest().click_answer(
        driver=driver, correct_answer=correct_answer, choices_dict=choices_dict
    )
    clear_output(wait=True)
    logging.info(' ')


def evaluate_all_pages(driver, highway_code_image_dict: dict):
    """
    Evaluates all the pages in the driving test using the evaluate_per_page func.
    Uses recursion to keep on evaluating pages until there is none left to evaluate.

    Parameters
    ----------
    driver: the selenium driver used to open the webpage and start the test.
    highway_code_image_dict: dict, a dict of Highway Code images.

    Returns
    -------
    All the pages evaluated in the driving theory test.

    """
    # Evaluate the page
    evaluate_per_page(
        driver, highway_code_image_dict=highway_code_image_dict
    )

    # Go onto next page
    next_page_button_id = "btn-next"
    driving_theory.StartTest().next_page(
        driver=driver, next_page_button_id=next_page_button_id
    )

    # Recursively complete all pages
    evaluate_all_pages(driver, highway_code_image_dict)


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

    # Initiate the logger
    logger_filepath = '/Users/aniruddha.sengupta/Desktop/Driving_Theory/logs'
    driving_theory.Logging().create_logging_config(filepath=logger_filepath)

    # Make an image bank of the highway code images
    logging.info("Making an image bank of Highway Code images")
    highway_code_url = "https://www.gov.uk/guidance/the-highway-code/traffic-signs"
    highway_code_image_dict = (
        driving_theory.ImageComparison().make_highway_code_image_dict(
            url=highway_code_url
        )
    )

    # Start the test
    logging.info('Starting the test')
    driver = driving_theory.StartTest().open_webpage(url=url, start_xpath=start_xpath)

    try:
        evaluate_all_pages(driver, highway_code_image_dict)
    except:
        logging.info('The test has now ended')


def main():
    """
    The main function.

    """
    complete_theory_test()


# Execution
if __name__ == "__main__":
    main()
