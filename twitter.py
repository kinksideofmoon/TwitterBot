import json

import config
from config import TwitterConfig
from config import Config
import logging
import pytwitter
from pytwitter import PyTwitterError
import tweepy
import time
from yaspin import yaspin

logging.basicConfig(format=Config.Logging.format, level=Config.Logging.level)


class User:
    __username = ""
    __id = ""
    __number_of_tweets = int

    def __init__(self, username, id, number_of_tweets):
        self.__username = username
        self.__id = id
        self.__number_of_tweets = number_of_tweets

    @property
    def username(self):
        return self.__username

    @username.setter
    def username_setter(self):
        raise Warning("The username value can be set only during the initialization of the object.")

    @property
    def id(self):
        return self.__id

    @id.setter
    def id_setter(self):
        raise Warning("The id value can be set only during the initialization of the object.")

    @property
    def number_of_tweets(self):
        return self.__number_of_tweets

    @number_of_tweets.setter
    def number_of_tweets_setter(self):
        raise Warning("The number_of_tweets value can be set only during the initialization of the object.")


class Twitter:
    __PyTwitterAPi = None
    __TweepyAPI = None
    __UserID = None
    Followers = None
    __isConnected = False

    class __Followers:

        __PyTwitterAPI = None
        __TweepyAPI = None
        __UserID = None

        __followers = []
        __last_followers = []
        __new_followers = []

        class __Follower(User):
            __followed_date = int

            def __init__(self, username, id, number_of_tweets=-1, followed_date=-1):
                super().__init__(username=username, id=id, number_of_tweets=number_of_tweets)
                self.__followed_date = followed_date

            @property
            def followed_date(self):
                return self.__followed_date

            @followed_date.setter
            def followed_date_setter(self):
                raise Warning("The followed_date value can be set only during the initialization of the object.")

        def __init__(self, PyTwitterAPI, TweepyAPI, UserID):
            self.__PyTwitterAPI = PyTwitterAPI
            self.__TweepyAPI = TweepyAPI
            self.__UserID = UserID

            self.__load_last_followers_from_csv(Config.last_followers_cache_file)
            self.__get_my_followers()
            self.__check_for_new_followers()

        def __get_my_followers(self):
            return self.__get_followers(self.__UserID)

        def new(self):
            _ = []
            for follower in self.__new_followers:
                _.append(follower.username)
            return _

        def all(self):
            _ = []
            for follower in self.__followers:
                _.append(follower.username)
            logging.debug("Return " + str(len(_)) + " followers.")
            return _

        # @yaspin(text="Getting followers...")
        def __get_followers(self, user_id: object) -> object:

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
                    response = self.__PyTwitterAPI.get_followers(user_id=user_id, pagination_token=next_token,
                                                                 max_results=config.TwitterConfig.max_results)
                    for user in response.data:
                        self.__setitem__(user.id, user.username)
                    next_token = response.meta.next_token
                    logging.debug("... get " + str(len(self)) + " followers.")
                    logging.debug("... next page token is: " + str(next_token))
                except PyTwitterError as ex:
                    if ex.message['title'] == "Too Many Requests":
                        logging.error("... failed, " + str(ex.message) + ", retrying " + str(number_of_try) +
                                      " after " + str(number_of_try * 60) + " sec.")
                        time.sleep(number_of_try * 60)
                    else:
                        raise ex
                else:
                    break
                finally:
                    if next_token is not None:
                        logging.debug("... waiting 30 sec to not overload Twitter API ...")
                        time.sleep(30)
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

        def __check_for_new_followers(self, user_id=__UserID):
            for follower in self.__followers:
                for last_follower in self.__last_followers:
                    if last_follower.id == follower.id:
                        break
                else:
                    self.__new_followers.append(follower)
            logging.info("Found " + str(len(self.__new_followers)) + " new followers.")

        def lost(self, user_id=__UserID):
            _ = []
            for last_follower in self.__last_followers:
                found_match = False
                for follower in self.__followers:
                    if last_follower.username == follower.username:
                        found_match = True
                        break
                if not found_match:
                    _.append(last_follower.username)
                    logging.debug("Lost " + last_follower.username)
            logging.debug("Found " + str(len(_)) + " lost followers")
            return _

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
                logging.info("... successfully load the file. Found " + str(len(self.__last_followers)) + " entries.")

        def __save_followers_to_csv(self, filename: str):
            with open(filename, 'w', encoding='utf-8', errors='ignore', newline='\n') as fp:
                fp.write("id;username;number_of_tweets;followed_date\n")
                for follower in self.__followers:
                    fp.write(str(follower.id) + ';' + str(follower.username) + ";" +
                             str(follower.number_of_tweets) + ";" + str(follower.followed_date) + "\n")

    class __Followings:

        __PyTwitterAPI = None
        __TweepyAPI = None
        __UserID = None

        __following = []

        class __Following(User):
            def __init__(self, username, id, number_of_tweets=-1):
                super().__init__(username=username, id=id, number_of_tweets=number_of_tweets)

        def __init__(self, PyTwitterAPI, TweepyAPI, UserID):
            self.__PyTwitterAPI = PyTwitterAPI
            self.__TweepyAPI = TweepyAPI
            self.__UserID = UserID

            self.__get_following(self.__UserID)

        def __setitem__(self, id, username, number_of_tweets=-1):

            for following in self.__following:
                if following.id == id:
                    break
            else:
                self.__following.append(self.__Following(username=username, id=id,
                                                         number_of_tweets=number_of_tweets))

        def __len__(self):
            return len(self.__following)

        def __iter__(self):
            raise NotImplemented

        def __get_paginated_following(self, next_token=None, user_id=__UserID):
            for number_of_try in range(1, 3):
                try:
                    logging.debug("Try " + str(number_of_try))
                    response = self.__PyTwitterAPI.get_following(user_id=user_id, pagination_token=next_token,
                                                                 max_results=config.TwitterConfig.max_results)
                    for user in response.data:
                        self.__following.append(self.__Following(username=user.username,
                                                                 id=user.id,
                                                                 number_of_tweets=-1))
                    next_token = response.meta.next_token
                    logging.debug("... get " + str(len(self)) + " following.")
                    logging.debug("... next page token is: " + str(next_token))
                except PyTwitterError as ex:
                    if ex.message['title'] == "Too Many Requests":
                        logging.error("... failed, " + str(ex.message) + ", retrying " + str(number_of_try) +
                                      " after " + str(number_of_try * 60) + " sec.")
                        time.sleep(number_of_try * 60)
                    else:
                        raise ex
                else:
                    break
                finally:
                    if next_token is not None:
                        logging.debug("... waiting 30 sec to not overload Twitter API ...")
                        time.sleep(30)
            return next_token

        def __get_following(self, user_id):
            logging.info("Trying to get the list of current following...")

            next_token = self.__get_paginated_following(user_id=self.__UserID, next_token=None)

            while next_token is not None:
                next_token = self.__get_paginated_following(next_token, user_id)

            logging.info("Get " + str(len(self)) + " following.")

            self.__save_following_to_csv(filename=Config.last_following_cache_file)

        def __save_following_to_csv(self, filename: str):
            with open(filename, 'w', encoding='utf-8', errors='ignore', newline='\n') as fp:
                fp.write("id;username;number_of_tweets\n")
                for following in self.__following:
                    fp.write(str(following.id) + ';' + str(following.username) + ";" +
                             str(following.number_of_tweets) + "\n")

        def all(self):
            _ = []
            for following in self.__following:
                _.append(following.username)
            logging.debug("Return " + str(len(_)) + " following.")
            return _

    @yaspin("Initializing Twitter client...")
    def __init__(self, config: TwitterConfig):
        self.__PyTwitterAPI = self.__connect_pytwitter(config)
        self.__TweepyAPI = self.__connect_tweepy(config)
        self.__UserID = self.__get_user_id
        self.Followers = self.__Followers(PyTwitterAPI=self.__PyTwitterAPI,
                                          TweepyAPI=self.__TweepyAPI,
                                          UserID=self.__UserID)
        self.Following = self.__Followings(PyTwitterAPI=self.__PyTwitterAPI,
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

    @yaspin("Tweeting image...")
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

    def get_private_messages(self):
        messages = self.__TweepyAPI.get_direct_messages
        print(json.dumps(messages))

    def two_side_followers(self):
        _ = []
        for following in self.Following.all():
            for follower in self.Followers.all():
                if following == follower:
                    _.append(follower)
                    break
        return _

    def to_follow_back(self):
        _ = []
        for follower in self.Followers.all():
            found_match = False
            for following in self.Following.all():
                if following == follower:
                    found_match = True
                    logging.debug("Found match - follower: " + follower + ", following: " + following)
                    break
            if not found_match:
                _.append(follower)
        logging.debug("Found " + str(len(_)) + " followers to follow back")
        return _
