import os
import pickle
from time import sleep
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium_stealth import stealth
from modules.base import Base
import pyperclip


class Parser(Base):
    URL = 'https://www.tiktok.com/'
    black_list = ['videootainment', ]

    def __init__(self, email, password, proxy=None, headless=False):
        super().__init__(proxy, headless)
        self.email = email
        self.password = password
        self.cookies_path = os.path.join(os.path.abspath('data'), 'cookies')
        self.cookies_file_path = os.path.join(self.cookies_path, f'{self.email}.pkl')
        self.actions = ActionChains(self.driver, duration=550)
        self.legacy_login = False

        os.makedirs(self.cookies_path, exist_ok=True)

        stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )

    def __input_keyword(self, keyword):
        # Find the input element using Selenium and input data into it
        search_input = self._wait_for_element_clickable(By.CSS_SELECTOR, 'input[data-e2e="search-user-input"]', 60)
        search_input.send_keys(keyword)

        # Press the Enter key
        search_input.send_keys(Keys.ENTER)

    def __parsing_processing(self, selector, timeout=5):
        # Waiting until the first element becomes clickable
        self._wait_for_element_clickable(By.XPATH, selector, 120)

        # Infinite scroll loop
        while True:
            # Scroll to the end of the page
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            sleep(timeout)

            # Retrieve current set of video links
            video_links = self.driver.find_elements(By.XPATH, selector)
            print('Found videos: ', len(video_links))

            # Break the loop if the count > 150
            if len(video_links) > 150:
                break


        # Extract video URLs from links
        video_urls = [link.get_attribute('href') for link in video_links]
        print(f'Total links: {len(video_urls)}\n')

        return video_urls

    def __parsing_scrolling(self, selector, timeout=5):
        video_urls = []

        # Find and click the button "for you"
        button = self._wait_for_element_clickable(By.XPATH, selector)
        button.click()
        sleep(30)

        # to create chains of actions
        achains = ActionChains(self.driver)

        # to create a page scroll using ARROW_DOWN
        body = self.driver.find_element(By.TAG_NAME, 'body')

        # create counter
        counter_page = 0

        # Infinite scroll loop
        while True:
            try:
                html_code = f'//article[@data-scroll-index="{counter_page}"]'
                # Waiting until the video becomes clickable
                element = self._wait_for_element_located(By.XPATH, html_code, 60)
                print(element)
                if self.legacy_login == True:
                    el = self._wait_for_element_located(By.TAG_NAME, "video", 20)

                    # find video, right click and copy link
                    element = self.driver.find_element(By.XPATH, "//video[@playsinline='true']")
                    # element = self.driver.find_element(By.TAG_NAME, "video")
                    # achains.context_click(right_click).perform()
                    achains.move_by_offset(100, 200).context_click().perform()
                achains.context_click(element).perform()
                sleep(timeout)
                self.driver.find_element(By.XPATH, "//span[contains(text(), 'Copy link')]").click()
                sleep(timeout)

                # save link
                copied_link = pyperclip.paste()
                video_urls.append(copied_link)
            except Exception as e:
                print(e)

            # Break the loop
            if len(video_urls) > 150:
                break

            # scroll loop
            body.send_keys(Keys.ARROW_DOWN)
            sleep(timeout)
            counter_page += 1  # update counter

        return video_urls

    def __save_links_to_file(self, links, file_path):
        try:
            # Attempt to open the file for appending, using UTF-8 encoding.
            with open(file_path, 'w', encoding='utf-8') as file:
                # Iterate through the provided links and write each one to a new line in the file.
                for link in links:
                    file.write(link + '\n')
                    file.flush()  # Flush the buffer to ensure immediate writing.

                # Display a success message indicating that the links were saved to the file.
                print("Links saved to file.")

        except Exception as e:
            # If an exception occurs during the file operation, print an error message.
            print(f"Error occurred while saving links: {str(e)}")

    @staticmethod
    def __cookies_file_exists(cookies_filename):
        return os.path.exists(cookies_filename)

    def login(self):
        try:
            print('Logging into the account...')

            # Navigate to the login URL
            self.driver.get(self.URL)

            # # # Find and click the login proposal
            # if self._wait_for_element_located(By.XPATH, "//button[.//div[text()='Log in']]"):
            #     self._wait_for_element_located(By.XPATH, "//button[.//div[text()='Log in']]").click()

            # Find and click the login proposal with phone/email/user_name
            step2 = self._wait_for_element_located(By.XPATH, "//*[contains(text(), 'Use phone / email / username')]")
            step2.click()
            sleep(5)

            # Find and click the login proposal with email
            step3 = self._wait_for_element_located(By.XPATH,
                                                   "//*[contains(text(), 'Log in with email or username')]")
            step3.click()
            sleep(5)

            # Find and fill in the email input field
            input_email = self._wait_for_element_located(By.XPATH, "//input[@placeholder='Email or username']")
            input_email.send_keys(self.email)
            sleep(5)

            # Find and fill in the password input field
            input_password = self._wait_for_element_located(By.XPATH, "//input[@placeholder='Password']")
            input_password.send_keys(self.password)
            sleep(5)

            # Find and click the login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-e2e="login-button"]')
            login_button.click()

            sleep(90)

            # Get the current session cookies and save them to a file
            cookies = self.driver.get_cookies()
            with open(self.cookies_file_path, "wb") as cookies_file:
                pickle.dump(cookies, cookies_file)
        except Exception as e:
            # Raise an exception in case of a login error
            raise Exception("Login error:", e)

    def parse_by_keyword(self, key, mode):
        """Mode: the recommendation, the following, the explore, find with keywords"""
        if mode == 'keywords':
            selector = '//div[@data-e2e="search_top-item"]//a[@tabindex="-1"]'  # top_tab_xpath
            self.__input_keyword(key)
            video_links = self.__parsing_processing(selector, 15)
        elif mode == 'explore':
            selector = '//div[@data-e2e="explore-item"]//a[@tabindex="-1"]'
            video_links = self.__parsing_processing(selector, 15)
        elif mode == 'following':
            button = ".//*[@data-e2e='nav-following']"
            video_links = self.__parsing_scrolling(button)
        else:
            button = ".//*[@data-e2e='nav-foryou']"
            video_links = self.__parsing_scrolling(button)

        save_path = os.path.join(self.results_path, key)
        os.makedirs(save_path, exist_ok=True)
        file_path = os.path.join(save_path, f'{key}.txt')

        sleep(30)

        self.__save_links_to_file(video_links, file_path)
