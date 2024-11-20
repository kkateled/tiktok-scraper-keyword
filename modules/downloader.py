import os.path

import requests
from selenium.webdriver.common.by import By

from modules.base import Base


class Downloader(Base):
    URL = 'https://snaptik.app/'

    def __init__(self, key, proxy=None, headless=False):
        super().__init__(proxy, headless)
        self.main_folder = os.path.join(self.results_path, key)
        self.links_file_path = os.path.join(self.main_folder, f'{key}.txt')

        # ensure that the folders exist
        os.makedirs(self.main_folder, exist_ok=True)

        # make the additional folders
        self.video_save_path = os.path.join(self.main_folder, f'{key}_videos')
        os.makedirs(self.video_save_path, exist_ok=True)

    def read_links_file(self):
        # handling the scenario where the file is not found
        if not os.path.isfile(self.links_file_path):
            print(f"File '{self.links_file_path} not found.")
            return []

        # reading data from the file and handling the scenario of an empty file
        with open(self.links_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            if not lines:
                print(f"File '{self.links_file_path}' is empty.")
                return []

        return lines

    def __input_url(self, link):
        # use the _wait_for_element_clickable method to wait until the input element with CSS selector 'input#url' is
        input_element = self._wait_for_element_clickable(By.CSS_SELECTOR, 'input#url')

        # use the send_keys method to input the specified 'link' into the found input element
        input_element.send_keys(link)

    def __get_normal_link(self):
        # find the element by its CSS selector
        download_link_element = self._wait_for_element_located(By.CSS_SELECTOR, 'a.button.download-file', 20)

        # extract the 'href' attribute, which contains the link
        download_link = download_link_element.get_attribute('href')

        return download_link

    @staticmethod
    def __download_video(url, save_path):
        try:
            # send  a get request  to the specified URL with streaming enabled
            response = requests.get(url, stream=True)
            response.raise_for_status()  # raise an HTTPError for bad responses

            print(f'Downloading video...')

            # open a file to save the video content
            with open(save_path, 'wb') as file:
                # iterate through the response content in chunks and write to the file
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            print('Video has been successfully downloaded and saved\n')
        except requests.exceptions.RequestException as e:
            # handle exceptions related to the requests library
            print(f'Error occurred while downloading the video: {e}')

    def download(self, link):
        # use the selenium WebDriver instance to navigate to a specified URL
        self.driver.get(self.URL)

        # calling the method to input the link into the search field
        self.__input_url(link)

        video_link = self.__get_normal_link()

        filename = f'{link.strip().split("/")[-1]}.mp4'  # extracting the last part of the URL after the last '/'
        file_save_path = os.path.join(self.video_save_path, filename)  # creating the full file save path

        # check if the video_link is not None
        if video_link:
            # call the method for downloading video using the final link
            self.__download_video(video_link, file_save_path)
        else:
            print("Failed to obtain the final video link")
