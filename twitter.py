import config
from config import TwitterConfig
from config import Config
import logging
import pytwitter
from pytwitter import PyTwitterError
import tweepy
import time

logging.basicConfig(format=Config.Logging.format, level=Config.Logging.level)


class Twitter:
    __PyTwitterAPi = None
    __TweepyAPI = None
    __UserID = None

    __isConnected = False

    class __Followers:

        __PyTwitterAPI = None
        __TweepyAPI = None
        __UserID = None

        __followers = []
        __last_followers = []
        __new_followers = []

        class __User:
            __username = ""
            __id = ""
            __number_of_tweets = int

            def __init__(self, username, id, number_of_tweets):
                self.username = username
                self.id = id
                self.number_of_tweets = number_of_tweets

            def username(self):
                return self.__username

            def id(self):
                return self.__id

            def number_of_tweets(self):
                return self.__number_of_tweets

        class __Follower(__User):
            __followed_date = int

            def __init__(self, username, id, number_of_tweets=-1, followed_date=-1):
                super().__init__(username=username, id=id, number_of_tweets=number_of_tweets)
                self.__followed_date = followed_date

            def followed_date(self):
                return self.__followed_date

        def __init__(self, PyTwitterAPI, TweepyAPI, UserID):
            self.__PyTwitterAPI = PyTwitterAPI
            self.__TweepyAPI = TweepyAPI
            self.__UserID = UserID

            self.__load_last_followers_from_csv(Config.last_followers_cache_file)

        def get_my_followers(self):
            return self.get_followers(self.__UserID)

        def get_followers(self, user_id):

            logging.info("Trying to get the list of current followers...")

            next_token = self.__get_paginated_followers(user_id=self.__UserID, next_token=None)

            while next_token is not None:
                next_token = self.__get_paginated_followers(next_token, user_id)

            logging.info("Get " + str(len(self)) + " followers.")

            self.__save_followers_to_csv(filename=Config.last_followers_cache_file)

        def __get_paginated_followers(self, next_token=None, user_id=__UserID):
            for number_of_try in range(1, 3):
                try:
                    logging.debug("Try " + str(number_of_try))
                    response = self.__PyTwitterAPI.get_followers(user_id=user_id, pagination_token=next_token)
                    for user in response.data:
                        self.__setitem__(user.id, user.username)
                    next_token = response.meta.next_token
                    logging.debug("... get " + str(len(self)) + " followers.")
                    logging.debug("... next page token is: " + str(next_token))
                except PyTwitterError as ex:
                    logging.error("... failed, " + str(ex.message) + "retrying " + str(number_of_try) +
                                  " after 60 sec.")
                else:
                    break
                finally:
                    logging.debug("... waiting 60 sec to not overload Twitter API ...")
                    if next_token is not None:
                        time.sleep(60)
            return next_token

        def __setitem__(self, id, username, number_of_tweets=-1, followed_date=-1):

            for follower in self.__followers:
                if follower.id == id:
                    break
            else:
                self.__followers.append(self.__Follower(username=username, id=id,
                                                        number_of_tweets=number_of_tweets,
                                                        followed_date=followed_date))

        def __len__(self):
            return len(self.__followers)

        def __iter__(self):
            raise NotImplemented

        def check_for_new_followers(self, user_id=__UserID):
            for follower in self.__followers:
                for last_follower in self.__last_followers:
                    if last_follower.id == follower.id:
                        break
                else:
                    self.__new_followers.append(follower)

        def __load_last_followers_from_csv(self, filename):

            logging.info("Load file: " + filename)
            try:
                with open(filename, 'r', encoding='utf-8', errors='ignore', newline='\n') as f:
                    for line in f:
                        logging.debug("---> File content: " + str(line.strip()))
                        follower_id, follower_name, number_of_tweets, followed_date = line.split(';')
                        self.__last_followers.append(self.__Follower(id=follower_id, username=follower_name,
                                                     number_of_tweets=-1, followed_date=0))
            except OSError as ex:
                logging.error("I/O error on file: " + filename + ": " + ex.strerror)
            except KeyError as ex:
                logging.error("Key error on loading the file: " + filename)
            finally:
                logging.info("... successfully load the file. Found " + str(self.__last_followers) + " entries.")

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

        def __save_followers_to_csv(self, filename: str):
            with open(filename, 'w', encoding='utf-8', errors='ignore', newline='\n') as fp:
                fp.write("id;username;number_of_tweets;followed_date\n")
                for follower in self.__followers:
                    fp.write(str(follower.id) + ';' + str(follower.username) + ";" +
                             str(follower.number_of_tweets) + ";" + str(follower.followed_date) + "\n")

    def __init__(self, config: TwitterConfig):
        self.__PyTwitterAPI = self.__connect_pytwitter(config)
        self.__TweepyAPI = self.__connect_tweepy(config)
        self.__UserID = self.__get_user_id
        self.Followers = self.__Followers(PyTwitterAPI=self.__PyTwitterAPI,
                                          TweepyAPI=self.__TweepyAPI,
                                          UserID=self.__UserID)

    def __connect_tweepy(self, config):
        try:
            __TweepyAPIAuth = tweepy.OAuthHandler(
                config.consumer_key,
                config.consumer_secret
            )
            __TweepyAPIAuth.set_access_token(
                config.access_token,
                config.access_secret
            )
        except Exception:
            self.__isConnected = False
            pass
        else:
            self.__isConnected = True

        return tweepy.API(__TweepyAPIAuth)

    def __connect_pytwitter(self, config):
        try:
            __PyTwitterAPI = pytwitter.Api(consumer_key=config.consumer_key,
                                           consumer_secret=config.consumer_secret,
                                           access_token=config.access_token,
                                           access_secret=config.access_secret,
                                           client_id=config.ClientID,
                                           client_secret=config.ClientSecret)
        except Exception:
            pass
            self.__isConnected = False
        else:
            self.__isConnected = True

        return __PyTwitterAPI
    @property
    def __get_user_id(self):
        if not self.__isConnected:
            logging.error("Not connected to Twitter")
        else:
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

