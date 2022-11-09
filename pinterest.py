import json
import random
import os.path
from py3pin.Pinterest import Pinterest

import urllib.request
import urllib.parse

import logging

from prettytable import PrettyTable
from tqdm import tqdm

from config import PinterestConfig
from config import Config

import extras

logging.basicConfig(format=Config.Logging.format, level=logging.ERROR)


def download_image(image_url: str, destination_dir="./img/"):
    a = urllib.parse.urlparse(image_url)
    image_filename = os.path.basename(a.path)

    image_file = None

    try:
        image_file = urllib.request.urlretrieve(image_url, destination_dir + image_filename)
    except:
        # ToDo: less generic exception
        image_filename = None

    return image_file, image_filename


class PinterestWrapper:

    __pinterest = None
    __username = None
    __boards = {}
    __pins = {}

    def __init__(self, email: str, username: str, password: str):
        self.__pinterest = Pinterest(email=email,
                                     password=password,
                                     username=username)

        self.__initialize_pinterest(username)

    def __init__(self, config: PinterestConfig):
        self.__pinterest: Pinterest = Pinterest(email=config.email,
                                                password=config.password,
                                                username=config.username)

        self.__initialize_pinterest(config.username)

    def __initialize_pinterest(self, username: str):
        self.__username = username
        self.__pinterest.login()
        self.__boards = self.__get_boards()
        self.__pins = self.__get_list_of_images_from_all_boards()

    def __del__(self):
        # self.logout()
        pass

    def __get_boards(self):
        _ = self.__pinterest.boards(username=self.__username)

        print("Found " + str(len(_)) + " boards:\n")

        x = PrettyTable()
        x.field_names = ["Board name", "Board ID"]
        for row in _:
            x.add_row([row["name"], row["id"]])
        print(x)

        extras.seep_with_progress_bar(60, 'Wait to not overload Pinterest API')
        return _

    def __get_list_of_images_from_all_boards(self):

        result = {}

        for board in tqdm(self.__boards, desc="Getting the list of images from all boards...", position=0):
            result[board['name']] = self.__get_list_of_images_from_board(board['id'])
            extras.seep_with_progress_bar(10, 'Wait to not overload Pinterest API')
        logging.debug("Found " + str(len(result)) + " pins.")

        # for row in result.keys():
        #     print(row + ": " + str(result[row]))

        # x = PrettyTable()
        # x.field_names = ["Board name", "Board ID"]
        #
        #
        # for row in result:
        #     # x.add_row([row["name"], row["id"]])
        #
        # print(x)

        return result

    def __get_list_of_images_from_board(self, board_id: str):

        _return = [1]
        pins = []

        logging.debug('Trying to fetch the data from the board ' + board_id)

        while _return:
            _return = self.__pinterest.board_feed(board_id=board_id)
            logging.debug("Get " + str(len(_return)) + " pins...")
            pins.extend(_return)
            extras.seep_with_progress_bar(10, 'Wait to not overload Pinterest API')
        return pins

    def download_random_image_from_board(self, board_name: str):
        url, src, title, description, board_link, board_name, pin = \
            self.get_url_of_random_image_from_list_pinterest(board_name)

        image_file, image_filename = download_image(url)

        return image_file, image_filename, src, title, description, board_link, board_name, pin

    def get_url_of_random_image_from_list_pinterest(self, board_name: str):

        pin = random.choice(self.__pins[board_name])
        image_url = str(pin['images']['orig']['url'])
        src = str(pin['link'])
        if (src is None or src == "") and pin["rich_summary"] is not None:
            src = str(pin["rich_summary"]["url"])
        if (src is None or src == "") and pin["attribution"] is not None:
            src = str(pin["attribution"]["url"])
        if (src is None or src == "") and pin["attribution"] is not None:
            src = str(pin["attribution"]["author_url"])
        if src is None or src == "":
            src = str(pin["link"])

        title = str(pin['title'])

        description = ""

        if pin["rich_summary"] is not None:
            description = str(pin['rich_summary']['display_description'])
        elif pin["description"] is not None:
            description = str(pin['description'])

        if description is None or description == "":
            description = str(pin['rich_summary']['display_name'])

        board_link = "https://pinterest.com" + str(pin['board']['url'])
        board_name = str(pin['board']['name'])
        return image_url, src, title, description, board_link, board_name, pin

    def other(self):


        src_link = str(pin['link'])


        if not src_link:
            src_link = 'Unknown'

        return image_file, src_link, board

    def logout(self):
        self.__pinterest.logout()


