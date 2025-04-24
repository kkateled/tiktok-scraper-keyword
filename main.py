import json
import os
from datetime import datetime
from traceback import print_exc
import sys


with open("config.json") as config_file:
    config = json.load(config_file)
tt_email = config["tt_email"]
tt_password = config["tt_password"]


def parsing(tag_path, mode):
    from modules.parser import Parser
    parser = Parser(tt_email, tt_password, proxy=os.getenv('PROXY'), headless=False)
    parser.login()
    parser.parse_by_keyword(tag_path, mode)
    parser.quit()


def downloading(file_tag):
    from modules.downloader import Downloader

    downloader = Downloader(file_tag, headless=True)
    links = downloader.read_links_file()

    for index, link in enumerate(links, 1):
        print(f"Processing link {index}/{len(links)}")
        try:
            downloader.download(link)
        except Exception as e:
            print(e)
            print_exc()


def create_project(file_tag, save_path):
    from modules.davinci_services import Davinci

    davinci = Davinci(file_tag)
    try:
        project = davinci.create_new_project()
        imported_clips = davinci.import_videos(project)
        davinci.create_timeline(project, imported_clips)
        # video_path = davinci.render(project, save_path)
        # return video_path
    except Exception as e:
        print_exc()
        sys.exit(1)


def youtube(media_file, client_secret):
    from modules.youtube_services import YouTube
    session = YouTube()
    youtube_id = session.authenticate(client_secret)
    session.upload_video(youtube_id, media_file)


if __name__ == "__main__":
    choice = input("Enter '1' for scraping main page, '2' for following page, '3' for explore page, '4' for finding with keyword: ")
    if choice == '1':
        tag = f"main_{datetime.now().strftime('%m.%d')}"
        parsing(tag, mode='recommendation')
        downloading(tag)
        create_project(tag, os.getenv('SAVE_PATH'))
        # youtube(video, os.getenv('CLIENT'))
    elif choice == '2':
        tag = f"following_{datetime.now().strftime('%m.%d')}"
        parsing(tag, mode='following')
        downloading(tag)
        create_project(tag, os.getenv('SAVE_PATH'))
        # youtube(video, os.getenv('CLIENT'))
    elif choice == '3':
        tag = f"explore_{datetime.now().strftime('%m.%d')}"
        parsing(tag, mode='explore')
        downloading(tag)
        create_project(tag, os.getenv('SAVE_PATH'))
        # youtube(video, os.getenv('CLIENT'))
    elif choice == '4':
        tag = input("Enter keyword for finding")
        if len(tag) != 0:
            parsing(tag, mode='keywords')
            downloading(tag)
            create_project(tag, os.getenv('SAVE_PATH'))
            # youtube(video, os.getenv('CLIENT'))
        else:
            print("Empty string")
    else:
        print("Invalid choice. Please enter '1', '2'")
