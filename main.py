import json
import os
import shutil
from datetime import date

os.environ["DBUS_SESSION_BUS_ADDRESS"] = "/dev/null"

with open("config.json") as config_file:
    config = json.load(config_file)

tt_email = config["tt_email"]
tt_password = config["tt_password"]


proxy = ''


def parsing(keywords):
    from modules.parser import Parser

    parser = Parser(tt_email, tt_password, proxy=None, headless=False)

    for key in keywords:
        parser.login()
        parser.parse_by_keyword(key)
    parser.quit()


def downloading(keywords):
    from modules.downloader import Downloader

    for key in keywords:
        downloader = Downloader(key, headless=True)
        links = downloader.read_links_file()

        for index, link in enumerate(links, 1):
            print(f"Processing link {index}/{len(links)}")
            downloader.download(link)


def delete(keywords):
    """
    Delete folder with videos. Save links.txt.
    """
    for key in keywords:
        mydir = os.path.join("/Users/kate/PycharmProjects/tiktokdownloader/results", key, f'{key}_videos')
        shutil.rmtree(mydir)


if __name__ == "__main__":
    keys = [
        date.today().strftime("%d.%m.%Y"),
    ]

    choice = input("Enter '1' to run the parser, '2' to run the downloader, '3' to run the cleaning: ")
    if choice == '1':
        parsing(keys)
    elif choice == '2':
        downloading(keys)
    elif choice == '3':
        delete(keys)
    else:
        print("Invalid choice. Please enter '1' or '2'")
