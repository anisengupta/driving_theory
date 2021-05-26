# Initial Config
import driving_theory
from IPython.display import clear_output

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
    print("Identifying the questions")
    question_class_name = "govuk-fieldset__heading"
    question = driving_theory.StartTest().identify_question(
        driver=driver, question_class_name=question_class_name, wait_time=10
    )

    # Identify the choices
    print("Identifying the choices")
    choice_class_name = "govuk-radios"
    choices = driving_theory.StartTest().identify_choices(
        driver=driver, choice_class_name=choice_class_name, wait_time=10
    )

    # Make a choices dict
    print("Making a choices dictionary")
    choices_dict = driving_theory.StartTest().make_choices_dict(choices=choices)

    # Obtain the answer from Google
    # If the question is pictorial, obtain the answer using the ImageDetection
    # & ImageSearch classes
    print("Detecting whether there is an image on the page")
    image_xpath = '//*[@id="main-content"]/div[1]/div/div[3]/div[1]/div[1]/div/div[2]/fieldset/div/div[1]/p/img'
    image_detection, image_body = driving_theory.ImageDetection().detect_image_question(
        driver=driver, image_xpath=image_xpath
    )
    if image_detection:
        print("Image on page detected")
        # If there is an image detected, obtain its URL
        print("Obtaining its URL")
        image_url = driving_theory.ImageDetection().get_image_url(image_body=image_body)

        # Lets see if we can use the ImageComparison class to obtain a caption
        # Obtain an initial answer
        print("Obtaining an answer for the image")
        threshold = 10
        answer = driving_theory.ImageComparison().get_sign_meaning(
            highway_code_image_dict=highway_code_image_dict,
            test_img_url=image_url,
            threshold=threshold,
        )

        # If the initial method doesnt find an answer, use the ImageSearch class
        if answer == "No caption found":
            print("No caption found for the image, opening a new tab")
            # Make a new tab
            driving_theory.ImageSearch().new_tab(driver=driver)

            # Switch control to the new tab opened
            print("Switching control to new tab")
            driving_theory.ImageSearch().switch_tab(driver=driver)

            # Open Google Image Search in the new tab
            print("Performing Google search")
            driver.get("https://www.google.com/imghp?hl=EN")

            # Accept the cookies
            try:
                print("Accepting the cookies")
                accept_button_xpath = '//*[@id="L2AGLb"]'
                driving_theory.ImageSearch().accept_google_search_cookies(
                    driver=driver, accept_button_xpath=accept_button_xpath, wait_time=1
                )
            except:
                print("Looks like the cookies have already been accepted, continuing")
                # Note that if an exception is returned, it means that
                # cookies are already accepted
                pass

            # Search for the image and obtain an answer
            print("Searching for the answer to the image")
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
            print(answer)

            # Close the tab opened
            print("Closing the tab")
            driving_theory.ImageSearch().close_tab(driver=driver)

            # Switch back control to the original tab
            print("Giving back control to the original tab")
            driving_theory.ImageSearch().switch_to_original_tab(driver=driver)
        else:
            print("Looks like the initial image answering method worked")
            # If the initial method using the ImageComparison class worked,
            # just use that as the answer
            answer = answer
            print(answer)
    else:
        print("Evaluating the choices_dict created")
        choices_dict_eval = driving_theory.StartTest().evaluate_choices_dict(
            choices_dict=choices_dict
        )
        print(choices_dict_eval)

        if choices_dict_eval:
            print("Looks like there are empty strings in the choices_dict")
            print("This means that the answers do not contain text, they contain images")
            # If the choices_dict_eval is True - it contains empty strings
            image_answers_class_name = "choice-image"
            print("Obtaining the image urls of the answers")
            image_urls = driving_theory.ImageDetection().detect_image_answers(
                driver=driver, image_answers_class_name=image_answers_class_name
            )

            # Identify whether the question being asked is a shape one
            print('Identifying whether the question being asked is a shape one')
            shape_question = driving_theory.StartTest().identify_shape_question(
                question=question
            )

            if shape_question:
                print('Looks like a shape question is detected')
                shapes = []

                print('Obtaining the shapes for the images')
                for image_url in image_urls:
                    shape = driving_theory.ImageComparison().detect_shape(image_url=image_url)
                    shapes.append(shape)

                print('Updating the choices_dict with the images shapes')
                choices_dict = driving_theory.ImageAnswers().update_choices_dict(captions=shapes)
            else:
                print(
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
                print(answer_outcome)
                print(answer)

                # Update the choices_dict accordingly
                if answer_outcome == "Answer obtained":
                    print("Looks like an answer was obtained")
                    # If an answer is obtained then update the choices_dict
                    print("Obtaining a list of captions")
                    captions = list(captions_dict.keys())
                    print(captions)

                    print("Updating the choices_dict")
                    choices_dict = driving_theory.ImageAnswers().update_choices_dict(
                        captions=captions
                    )
                else:
                    print("An answer was not obtained, keeping the choices_dict the same")
                    # If no answer is obtained then do not change the choices_dict
                    choices_dict = choices_dict

        # If no image is detected, then use the AnswerSearch class instead
        print("Looks like there are no images detected")
        try:
            # Try to obtain the correct answer
            print("Attempting to obtain a correct answer")
            answer = driving_theory.AnswerSearch().answer_search(question=question)
        except:
            print("It looks an answer cannot be obtained, choosing a random one")
            # If an answer cannot be obtained, choose a random one
            answer = driving_theory.CorrectAnswer().random_answer(
                choices_dict=choices_dict
            )

    # Obtain the correct answer amongst the choices
    print("Attempting to obtain a correct answer amongst the choices")
    correct_answer = driving_theory.CorrectAnswer().obtain_correct_answer(
        question=question, answer=answer, choices_dict=choices_dict
    )

    # Click on the answer
    print("Clicking on the answer")
    driving_theory.StartTest().click_answer(
        driver=driver, correct_answer=correct_answer, choices_dict=choices_dict
    )
    clear_output(wait=True)


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
    # Make an image bank of the highway code images
    print("Making an image bank of Highway Code images")
    highway_code_url = "https://www.gov.uk/guidance/the-highway-code/traffic-signs"
    highway_code_image_dict = (
        driving_theory.ImageComparison().make_highway_code_image_dict(
            url=highway_code_url
        )
    )

    # Evaluate the page
    evaluate_per_page(driver, highway_code_image_dict=highway_code_image_dict)

    # Go onto next page
    next_page_button_id = "btn-next"
    driving_theory.StartTest().next_page(
        driver=driver, next_page_button_id=next_page_button_id
    )

    # Recursively complete all pages
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
