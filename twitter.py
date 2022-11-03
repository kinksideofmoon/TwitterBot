from config import TwitterConfig
from config import Config
import logging
import pytwitter
import tweepy
import time


class Twitter:

    __PyTwitterAPi = None
    __TweepyAPI = None
    __UserID = None

    def __init__(self, config: TwitterConfig):
        self.__PyTwitterAPI = None
        self.__TweepyAPI = None
        self.__UserID = None

        if config:
            self.connect(config)

    def connect(self, config: TwitterConfig):
        self.__connect_pytwitter(config)

        self.__connect_tweepy(config)

        self.__UserID = self.__get_user_id()

    def __connect_tweepy(self, config):
        __TweepyAPIAuth = tweepy.OAuthHandler(
            config.consumer_key,
            config.consumer_secret
        )
        __TweepyAPIAuth.set_access_token(
            config.access_token,
            config.access_secret
        )
        self.__TweepyAPI = tweepy.API(__TweepyAPIAuth)

    def __connect_pytwitter(self, config):
        self.__PyTwitterAPI = pytwitter.Api(consumer_key=config.consumer_key,
                                            consumer_secret=config.consumer_secret,
                                            access_token=config.access_token,
                                            access_secret=config.access_secret,
                                            client_id=config.ClientID,
                                            client_secret=config.ClientSecret)

    def __get_user_id(self):

        try:
            response = self.__PyTwitterAPI.get_me()

        except:
            pass
        else:
            logging.debug(
                "Logged to Twitter as " + response.data.name + " (@" + response.data.username + ") with user id: " +
                response.data.id)

            return response.data.id

    def tweet_image(self, image_file: str, tweet: str):

        try:
            media = self.__TweepyAPI.media_upload(image_file)
            self.__PyTwitterAPI.create_tweet(text=tweet, media_media_ids=[str(media.media_id)],
                                             media_tagged_user_ids=[])
        except:
            # ToDo: add non-generic exception and exception handling
            pass
        else:
            logging.debug('Media ID: ' + str(media.media_id))

    def get_my_followers(self):
        self.get_followers(self.__UserID)

    def get_followers(self, user_id):

        # ToDo: refactor this method to be more clear

        logging.info("Trying to get the list of current followers...")

        followers = []
        try:
            response = self.__PyTwitterAPI.get_followers(user_id=user_id)
            followers += response.data
            logging.debug("... get " + str(len(response.data)) + " followers.")
            next_token = response.meta.next_token
            if next_token is None:
                logging.debug("... no next page token, finishing the task.")
            else:
                logging.debug("... next page token is: " + next_token)
                logging.debug("... waiting 60 sec to not overload Twitter API ...")
                time.sleep(60)

            while next_token is not None:
                response = self.__PyTwitterAPI.get_followers(user_id=user_id, pagination_token=next_token)
                followers += response.data

                logging.debug("... get another " + str(len(response.data)) + " followers.")

                next_token = response.meta.next_token
                logging.debug("... next page token is: " + str(next_token))

                if next_token is None:
                    logging.debug("... no next page token, finishing the task.")
                    break
                else:
                    logging.debug("... waiting 60 sec to not overload Twitter API ...")
                    time.sleep(60)
        except Exception as ex:
            logging.error("... failed, " + ex)

        logging.info("Get " + str(len(followers)) + " followers.")

        return followers

    def check_for_new_followers(self, user_id):
        pass

    def get_following(self, user_id):

        logging.info("Get following users...")
        following = []
        response = self.__PyTwitterAPI.get_following(user_id=user_id)
        following += response.data
        next_token = response.meta.next_token

        if next_token is None:
            logging.debug("... no next page token, finishing the task.")
        else:
            logging.debug("... waiting 60 sec to not overload Twitter API ...")
            time.sleep(60)
        while next_token is not None:

            try:
                response = self.__PyTwitterAPI.get_following(user_id=user_id, pagination_token=next_token)
            except Exception as ex:
                logging.error("... failed, " + ex)

            following += response.data

            logging.debug("... get another " + str(len(response.data)) + " following.")

            next_token = response.meta.next_token
            logging.debug("... next page token is: " + str(next_token))

            if next_token is None:
                logging.debug("... no next page token, finishing the task.")
                break
            else:
                logging.debug("... waiting 60 sec to not overload Twitter API ...")
                time.sleep(60)
        logging.info("Get " + str(len(following)) + " following.")

        return following

    def check_for_new_following(self, user_id):
        pass

    def __save(self, data, filename=Config.last_followers_cache_file):
        with open(filename, 'w', encoding='utf-8', errors='ignore', newline='\n') as fp:
            for item in data:
                fp.write(item.id + ';' + item.username + "\n")

    def __load(self, filename=Config.last_followers_cache_file):
        result = {}
        with open(filename, 'r', encoding='utf-8', errors='ignore', newline='\n') as fp:
            lines = fp.readlines()
            for line in lines:
                user_id, username = line.split(';')
                result[user_id] = username.strip()
            return result