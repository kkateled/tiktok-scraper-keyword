import json
import os
import shutil
from datetime import datetime


os.environ["DBUS_SESSION_BUS_ADDRESS"] = "/dev/null"

with open("config.json") as config_file:
    config = json.load(config_file)

tt_email = config["tt_email"]
tt_password = config["tt_password"]


proxy = ''


def parsing(keywords, mode):
    from modules.parser import Parser

    parser = Parser(tt_email, tt_password, proxy=None, headless=False)

    for key in keywords:
        parser.login()
        parser.parse_by_keyword(key, mode)
    parser.quit()


def downloading(keywords):
    from modules.downloader import Downloader

    for key in keywords:
        downloader = Downloader(key, headless=True)
        links = downloader.read_links_file()

        for index, link in enumerate(links, 1):
            print(f"Processing link {index}/{len(links)}")
            try:
                downloader.download(link)
            except Exception as e:
                print(e)


def delete(keywords):
    """
    Delete folder with videos. Save links.txt.
    """
    for key in keywords:
        del_dir = os.path.join("/Users/kate/PycharmProjects/tiktokdownloader/results", key, f'{key}_videos')
        shutil.rmtree(del_dir)


if __name__ == "__main__":
    keys = [
        datetime.now().strftime('%m.%d'),
    ]

    choice = input("Enter '1' to run the parser, '2' to run the downloader, '3' to run the cleaning: ")
    if choice == '1':
        mode = input("Enter '1' the recommendation, '2' the all explore, '3' find with keywords: ")
        if mode == '1':
            parsing(keys, mode='recommendation')
        elif mode == '2':
            parsing(keys, mode='explore')
        elif mode == '3':
            parsing(keys, mode='keywords')
        else:
            print("Invalid choice. Please enter '1' or '2'")
    elif choice == '2':
        name_direct = input("Enter name of folders: ")
        downloading(list(name_direct.split(',')))
    elif choice == '3':
        name_direct = input("Enter name of folders: ")
        delete(list(name_direct.split(',')))
    else:
        print("Invalid choice. Please enter '1', '2' or '3'")
