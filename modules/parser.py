import os
import pickle
from time import sleep

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from modules.base import TikTok


class Parser(TikTok):
    URL = 'https://www.tiktok.com/'
    LOGIN_URL = 'https://www.tiktok.com/login/phone-or-email/email'

    def __init__(self, email, password, proxy=None, headless=False):
        super().__init__(proxy, headless)
        self.email = email
        self.password = password
        self.cookies_path = os.path.join(os.path.abspath('data'), 'cookies')
        self.cookies_file_path = os.path.join(self.cookies_path, f'{self.email}.pkl')

        os.makedirs(self.cookies_path, exist_ok=True)

    def __input_keyword(self, keyword):
        # Find the input element using Selenium and input data into it
        search_input = self._wait_for_element_clickable(By.CSS_SELECTOR, 'input[data-e2e="search-user-input"]', 60)
        search_input.send_keys(keyword)

        # Press the Enter key
        search_input.send_keys(Keys.ENTER)

    def __switch_to_video_tab(self):
        # Find and click the video tab
        video_tab = self.driver.find_element(By.ID, 'tabs-0-tab-search_video')
        video_tab.click()

    def __parsing_processing(self, selector, timeout=5):
        # Waiting until the first element becomes clickable
        self._wait_for_element_clickable(By.XPATH, selector, 120)

        # Find initial set of video links
        video_links = self.driver.find_elements(By.XPATH, selector)
        prev_video_count = len(video_links)

        # Infinite scroll loop
        while True:
            # Scroll to the end of the page
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            sleep(timeout)

            # Retrieve current set of video links
            video_links = self.driver.find_elements(By.XPATH, selector)
            current_video_count = len(video_links)
            print('Found videos: ', len(video_links))

            # Break the loop if the count remains the same (no new videos loaded)
            if current_video_count == prev_video_count:
                break

            # On each iteration, we update the value of 'prev_video_count'
            # by assigning it the value of 'current_video_count'
            prev_video_count = current_video_count

        # Extract video URLs from links
        video_urls = [link.get_attribute('href') for link in video_links]
        print(f'Total links: {len(video_urls)}\n')

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
        # Check if cookies file exists
        if self.__cookies_file_exists(self.cookies_file_path):
            print('Cookies found. Logging into the account with the cookies...')

            # Load cookies from the existing file
            with open(self.cookies_file_path, "rb") as cookies_file:
                cookies = pickle.load(cookies_file)

            # Navigate to the login URL and add cookies to the current session
            self.driver.get(self.LOGIN_URL)
            for cookie in cookies:
                self.driver.add_cookie(cookie)

            # Refresh the page after adding cookies
            self.driver.get(self.LOGIN_URL)
        else:
            try:
                print('Logging into the account...')

                # Navigate to the login URL
                self.driver.get(self.LOGIN_URL)

                # Find and fill in the email input field
                input_email = self._wait_for_element_located(By.CSS_SELECTOR, 'input[type="text"]')
                input_email.send_keys(self.email)

                # Find and fill in the password input field
                input_password = self._wait_for_element_located(By.CSS_SELECTOR, 'input[type="password"]')
                input_password.send_keys(self.password)

                # Find and click the login button
                login_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-e2e="login-button"]')
                login_button.click()

                sleep(30)

                # Wait for the login button to become invisible (indicating successful login)
                self._wait_for_element_invisible(By.CSS_SELECTOR, 'button[data-e2e="login-button"]')

                # Get the current session cookies and save them to a file
                cookies = self.driver.get_cookies()
                with open(self.cookies_file_path, "wb") as cookies_file:
                    pickle.dump(cookies, cookies_file)
            except Exception as e:
                # Raise an exception in case of a login error
                raise Exception("Login error: \n", e)

    def parse_by_keyword(self, key, mode='top'):
        save_path = os.path.join(self.results_path, key)
        os.makedirs(save_path, exist_ok=True)

        file_path = os.path.join(save_path, f'{key}.txt')

        self.driver.get(self.URL)
        self.__input_keyword(key)
        sleep(60)

        # XPath expressions for finding links on the Top and Videos tabs
        top_tab_xpath = '//div[@data-e2e="search_top-item"]//a[@tabindex="-1"]'
        video_tab_xpath = '//div[@data-e2e="search_video-item"]//a[@tabindex="-1"]'

        if mode == 'top':
            video_links = self.__parsing_processing(top_tab_xpath, 15)
        else:
            video_links = self.__parsing_processing(video_tab_xpath, 15)

        self.__save_links_to_file(video_links, file_path)

