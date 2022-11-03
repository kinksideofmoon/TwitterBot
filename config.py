import logging


class TwitterConfig:
    ClientID = 'WEdGSVh0Q2JsRGRwazRjTFI2TWI6MTpjaQ'
    ClientSecret = 'M84XPa7zqEloiPq5jEBrmNpZoh2rPw0GLtSslhbMcUnEUmBmQA'
    consumer_key = 'WVYpqfk1HWQyJkmW0gHdL3Eef'
    consumer_secret = 'F3a5sauFEmmtMrJy29DSooVThttfIAOxjNEUmFOEywBDGRWH6O'
    access_token = '3412500364-4nvgHRMF7QkWIn8qUxwXuxt54rDxOCRFRwweaDk'
    access_secret = 'HEzL386HjQo1kpONPMxvZ6cd4sQQrEYCCleaVXs9h45jS'


class PinterestConfig:
    email = 'pawel.wojtal@gmail.com'
    password = 'OperaGloves1^'
    username = 'KinkSideOfTheMoon'


class LoggingConfig:
    format = '%(funcName)s:%(levelname)s: %(message)s'
    level = logging.DEBUG


class TelegramConfig:
    api_id = '15194207'
    api_hash = 'ae48649a5561b9f9d76163a5c22d8d35'
    token = '5555538687:AAGH6R5PDfW8E8R50UDx5G3tjF3X6QGTdVU'
    phone = '+48503114736'


class Config:
    Logging = LoggingConfig
    Twitter = TwitterConfig
    Pinterest = PinterestConfig
    Telegram = TelegramConfig

    temp_dir = './img/'
    cache_dir = './cache/'

    last_followers_cache_file = cache_dir + 'last_followers.csv'
