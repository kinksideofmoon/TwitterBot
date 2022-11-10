import logging
import os


class TwitterConfig:
    ClientID = ""
    ClientSecret = ""
    consumer_key = ""
    consumer_secret = ""
    access_token = ""
    access_secret = ""

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

        print("Twitter configuration:\n"
              "  ClientID: " + self.ClientID + "\n"
              "  Client Secret: " + self.ClientSecret + "\n"
              "  ----- \n"
              "  Consumer Key: " + self.consumer_key + "\n"
              "  Consumer Secret: " + self.consumer_secret + "\n"
              "  ----- \n"
              "  Access Token: " + self.access_token + "\n"
              "  Access Secret: " + self.access_secret
              )


class PinterestConfig:
    email = ""
    username = ""
    password = ""

    def __init__(self):
        try:
            self.email = os.environ.get('pinterest_email')
            self.username = os.environ.get('pinterest_username')
            self.password = os.environ.get('pinterest_password')

            print("Pinterest configuration:\n"
                  " email: " + self.email + "\n"
                                            " username: " + self.username + "\n"
                                                                            " password: " + self.password)

        except KeyError:
            print("Pinterest Configuration is not ready. Please set OS variables:\n "
                  " - pinterest_email\n"
                  " - pinterest_username \n"
                  " - pinterest_password")


class LoggingConfig:
    format = '%(funcName)s:%(levelname)s: %(message)s'
    level = logging.INFO


class TelegramConfig:

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

    last_followers_cache_file = cache_dir + 'last_followers.csv'
