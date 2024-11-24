import json
import os
from datetime import datetime
import sys


with open("config.json") as config_file:
    config = json.load(config_file)
tt_email = config["tt_email"]
tt_password = config["tt_password"]


def parsing(tag_path, mode):
    from modules.parser import Parser

    parser = Parser(tt_email, tt_password, proxy=None, headless=False)
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
        print(f"Error: {str(e)}")
        sys.exit(1)


def youtube(media_file, client_secret):
    from modules.youtube_services import YouTube
    session = YouTube()
    youtube_id = session.authenticate(client_secret)
    session.upload_video(youtube_id, media_file)


if __name__ == "__main__":
    choice = input("Open DaVinci. Enter '1' for Monster, '2' for Frostbite: ")
    if choice == '1':
        tag = f"monster_{datetime.now().strftime('%m.%d')}"
        parsing(tag, mode='recommendation')
        downloading(tag)
        create_project(tag, os.getenv('SAVE_PATH_MONSTER'))
        # youtube(video, os.getenv('CLIENT_MONSTER'))
    elif choice == '2':
        tag = f"frostbite_{datetime.now().strftime('%m.%d')}"
        parsing(tag, mode='following')
        downloading(tag)
        create_project(tag, os.getenv('SAVE_PATH_FROSTBITE'))
        # youtube(video, os.getenv('CLIENT_FROSTBITE'))
    else:
        print("Invalid choice. Please enter '1', '2'")
