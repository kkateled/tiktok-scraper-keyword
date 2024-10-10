import json
import os
import shutil

os.environ["DBUS_SESSION_BUS_ADDRESS"] = "/dev/null"

with open("config.json") as config_file:
    config = json.load(config_file)

tt_email = config["tt_email"]
tt_password = config["tt_password"]


proxy = ''


def parsing():
    from modules.parser import Parser

    parser = Parser(tt_email, tt_password, proxy=None, headless=False)

    parser.login()
    parser.parse()
    parser.quit()


def parsing_keys(keywords):
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

    ]

    choice = input("Enter '1' to run the parser, '2' to run the downloader, '3' to run the cleaning: ")
    if choice == '1':
        mode = input("Enter '1' to run the parser without keywords, '2' with ones: ")
        if mode == '1':
            parsing()
        elif mode == '2':
            parsing_keys(keys)
        else:
            print("Invalid choice. Please enter '1' or '2'")
    elif choice == '2':
        name_direct = input("Enter name of folder: ")
        downloading(name_direct)
    elif choice == '3':
        name_direct = input("Enter name of folder: ")
        delete(name_direct)
    else:
        print("Invalid choice. Please enter '1', '2' or '3'")
