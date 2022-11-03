import logging
from tqdm import tqdm
import extras
import random

from config import Config
from twitter import Twitter
from pinterest import PinterestWrapper


logging.basicConfig(format=Config.Logging.format, level=Config.Logging.level)

tweets = {
    "Opera Gloves": "#operagloves #longgloves #gloves #LatexEvil",
    "Thigh boots": "#thighboots #boots #thigh #overknees #overknee #LatexEvil"
}

boards_ids = ['Opera Gloves', 'Thigh boots']

localconfig = Config()

__twitter = Twitter(localconfig.Twitter)
__pinterest = PinterestWrapper(localconfig.Pinterest)


def get_random_images_from_pinterest_and_tweet_them(number_of_image_to_be_posted: int, board="Opera Gloves"):
    for _ in tqdm(range(0, number_of_image_to_be_posted - 1), desc="Get random images from pinterest and tweet them"):

        image_file, image_filename, src_link = __pinterest.download_random_image_from_board(board)

        if src_link is None or src_link == "":
            src_link = "Unknown"

        __twitter.tweet_image(image_file=image_file[0],
                              tweet=tweets[board] + "\nSource: " + src_link)

        extras.seep_with_progress_bar(60, "Waiting to not overload Twitter API...")


get_random_images_from_pinterest_and_tweet_them(10, random.choice(boards_ids))

