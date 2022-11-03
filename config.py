import logging


class TwitterConfig:
    ClientID = 'xxx'
    ClientSecret = 'xxx'
    consumer_key = 'xxx'
    consumer_secret = 'xxx'
    access_token = 'xxx'
    access_secret = 'xxx'


class PinterestConfig:
    email = 'xxx'
    password = 'xxx'
    username = 'xxx'


class LoggingConfig:
    format = '%(funcName)s:%(levelname)s: %(message)s'
    level = logging.DEBUG


class TelegramConfig:
    api_id = 'xxx'
    api_hash = 'xxx'
    token = 'xxx'
    phone = 'xxx'


class Config:
    Logging = LoggingConfig
    Twitter = TwitterConfig
    Pinterest = PinterestConfig
    Telegram = TelegramConfig

    temp_dir = './img/'
    cache_dir = './cache/'

    last_followers_cache_file = cache_dir + 'last_followers.csv'
