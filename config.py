import logging
import os
from yaspin import yaspin


class TwitterConfig:
    ClientID = ""
    ClientSecret = ""
    consumer_key = ""
    consumer_secret = ""
    access_token = ""
    access_secret = ""

    @yaspin(text="Loading Twitter configuration")
    def __init__(self):
        try:
            self.ClientID = os.environ.get("twitter_clientid")
            self.ClientSecret = os.environ.get("twitter_clientsecret")
            self.consumer_key = os.environ.get("twitter_consumerkey")
            self.consumer_secret = os.environ.get("twitter_consumersecret")
            self.access_token = os.environ.get("twitter_accesstoken")
            self.access_secret = os.environ.get("twitter_accesssecret")

            if self.ClientID is None:
                raise ValueError("Twitter API Client ID is empty")

            if self.ClientSecret is None:
                raise ValueError("Twitter API Client Secret is empty")

            if self.consumer_key is None:
                raise ValueError("Twitter API Consumer Key is empty")

            if self.consumer_secret is None:
                raise ValueError("Twitter API Consumer Secret is empty")

            if self.access_token is None:
                raise ValueError("Twitter API Access Token is empty")

            if self.access_secret is None:
                raise ValueError("Twitter API Access Secret is empty")

        except KeyError:
            print("Incorrect Twitter configuration. Please set the OS Env variables:\n"
                  " - twitter_clientid\n"
                  " - twitter_clientsecret")


class PinterestConfig:
    email = ""
    username = ""
    password = ""

    @yaspin(text="Loading Pinterest configuration")
    def __init__(self):
        try:
            self.email = os.environ.get('pinterest_email')
            self.username = os.environ.get('pinterest_username')
            self.password = os.environ.get('pinterest_password')

        except KeyError:
            print("Pinterest Configuration is not ready. Please set OS variables:\n "
                  " - pinterest_email\n"
                  " - pinterest_username \n"
                  " - pinterest_password")


class LoggingConfig:
    format = '%(funcName)s:%(levelname)s: %(message)s'
    level = logging.ERROR


class TelegramConfig:
    @yaspin(text="Loading Telegram configuration")
    def __init__(self):
        try:
            self.api_id = os.environ.get('telegram_apiid')
            self.api_hash = os.environ.get('telegram_apihash')
            self.token = os.environ.get('telegram_token')
            self.phone = os.environ.get('telegram_phone')
            self.chat_id = os.environ.get('telegram_chatid')
        except KeyError:
            print("Telegrom Configuration is not ready. Please set OS variables:\n "
                  " - telegram_apiid\n"
                  " - telegram_apihash\n"
                  " - telegram_token\n"
                  " - telegram_phone\n"
                  " - telegram_chatid")


class Config:
    Logging = LoggingConfig
    Twitter = TwitterConfig()
    Pinterest = PinterestConfig()
    Telegram = TelegramConfig

    temp_dir = './img/'
    cache_dir = './cache/'

    print("Configuration:")

    if not os.path.exists(temp_dir):
        print("\t" + temp_dir + " not exists, trying to create one...")
        os.mkdir(temp_dir)
        print("\t\t... done.")
    else:
        print("\tFound temp_dir: " + temp_dir)

    if not os.path.exists(cache_dir):
        print("\t" + cache_dir + " not exists, trying to create one...")
        os.mkdir(cache_dir)
        print("\t\t... done.")
    else:
        print("\tFound cache_dir: " + cache_dir)

    last_followers_cache_file = cache_dir + 'last_followers.csv'

    assert (os.path.exists(temp_dir), temp_dir + " not found")
    assert (os.path.exists(cache_dir), cache_dir + " not found")
    assert (os.path.exists(last_followers_cache_file), last_followers_cache_file + " not found!")
