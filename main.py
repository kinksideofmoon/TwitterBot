import json
import logging
from tqdm import tqdm

import config
import extras
import random

from config import Config
from twitter import Twitter
from pinterest import PinterestWrapper
from telegram import Telegram

logging.basicConfig(format=Config.Logging.format, level=Config.Logging.level)

tweets = {
    "Opera Gloves": "#operagloves #longgloves #gloves #LatexEvil",
    "Thigh boots": "#thighboots #boots #thigh #overknees #overknee #LatexEvil"
}

telegram_client = Telegram(config.TelegramConfig())

boards_ids = ['Opera Gloves', 'Thigh boots']

chosen_board = random.choice(boards_ids)

response = telegram_client.send("Start with board " + chosen_board)

localconfig = Config()

__twitter = Twitter(localconfig.Twitter)

# __twitter.get_private_messages()
#

string_to_send = "<b>New followers: </b>"

for follower in __twitter.Followers.new():
    string_to_send = string_to_send + "\nhttps://twitter.com/" + follower

telegram_client.send(string_to_send)

string_to_send = "----------------------\nLost followers:"

for follower in __twitter.Followers.lost():
    string_to_send = string_to_send + "\nhttps://twitter.com/" + follower

telegram_client.send(string_to_send)

string_to_send = "----------------------\n<b>To follow back:</b>"

for follower in __twitter.to_follow_back():
    string_to_send = string_to_send + "\nhttps://twitter.com/" + follower

telegram_client.send(string_to_send)

__pinterest = PinterestWrapper(localconfig.Pinterest)


def get_random_images_from_pinterest_and_tweet_them(number_of_image_to_be_posted: int, board="Opera Gloves"):
    for _ in tqdm(range(0, number_of_image_to_be_posted - 1), desc="Get random images from pinterest and tweet them"):

        image_file, image_filename, src_link, title, description, \
            board_link, board_name, pin = __pinterest.download_random_image_from_board(board)

        assert type(image_file) is not None, "Image file should not be None"
        assert type(image_filename) is not None, "image_filename should not be None"

        if src_link is None or src_link == "" or src_link == "None":
            telegram_client.send("Found picture without source, skipped")
            telegram_client.send("Source: " + src_link + "\nTitle: " + title + "\nDesc: " + description + "\n"
                                                         "Board link: " + board_link + "\nBoard name: " + board_name)

            telegram_client.send_photo(Config.temp_dir + image_filename)
            telegram_client.send("End of pic---<")

        else:
            telegram_client.send("Source: " + src_link + "\nTitle: " + title + "\nDesc: " + description + "\n"
                                 "Board link: " + board_link + "\nBoard name: " + board_name)

            telegram_client.send_photo(Config.temp_dir + image_filename)

            __twitter.tweet_image(image_file=image_file[0],
                                  tweet=tweets[board] + "\nSource: " + src_link + "\n" + title + "\n" +
                                  description + "\n")

            extras.seep_with_progress_bar(240, "Waiting to not overload Twitter API...")


get_random_images_from_pinterest_and_tweet_them(50, chosen_board)

telegram_client.send("...End")
