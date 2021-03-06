#!/usr/bin/env python

#
# freecaykes
# https://github.com/freecaykes
#

"""
script to fetch twitter feed from list of handlers in twitter_handles to post on
the specified subreddit
"""

import os
import sys
import json
import string
import signal
from threading import Timer

import praw
import tweepy

import error
from get_access_token import get_access_token
from ParallelSBTree import ParallelSBTree


twitter_posts = ParallelSBTree({})
handles_in_a_tree = ParallelSBTree({})
defaults = "./twitter_handles.json"
configuration  = "./configure.json"

handle_list_key = ""
subreddit_str = ""
reddit_url = "https://reddit.com/"
twitter_url = "https://twitter.com/"

GET_INTERVAL = 300  # 5 minutes avoid choosing too low of number - RateLimitError
UTF_8 = 'utf-8'


#
# write to json file in file_src
#
def update_json(file_src, keys, values):
    with open(file_src, "r+") as json_src:
        json_root = json.load(json_src)
        for i in range(0, len(keys)):
            json_root[keys[i]] = values[i]
        # write update
        json_src.close()
        json_src = open(file_src, "w+")
        json_src.write(json.dumps(json_root))


#
# initialize OAUTH with twitter api
#
def setup_twitter_api(consumer_key, consumer_secret, access_token, access_key, username, password):
    if access_token == "" or access_key == "":
        (access_token, access_key) = get_access_token(consumer_key, consumer_secret, username, password)
        #  update config  file
        update_json(configuration, ["TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_KEY"], [access_token, access_key])

    twitter_api = None
    try:    # authorize twitter, initialize tweepy
       auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
       auth.set_access_token( access_token, access_key)
       twitter_api = tweepy.API(auth)
    except tweepy.TweepError:
       print error.AUTH_ERROR

    return twitter_api


#
# authorize reddit OAUTH initialize praw
#
def setup_reddit_api(client_id, client_secret, password, user_agent, username):
    reddit_api = None
    try:
        reddit_api = praw.Reddit(client_id=client_id, client_secret=client_secret,
                         password=password, user_agent=user_agent,
                         username=username)
    except OAuthException:
        print error.AUTH_ERROR

    return reddit_api


#
# fetch twitter top tweet from account
#
def get_tweet(twitter_api, account):
    global twitter_handles, twitter_posts

    recent_user_tweet = twitter_api.user_timeline(screen_name = str(account['handle']) ,count=1)[0]
    # print recent_user_tweet
    print account
    print "tweet_id:", recent_user_tweet.id,  "user_id:", str(account['max_id'])
    if recent_user_tweet.id > int( str(account['max_id']) ):
        tweet_url = twitter_url + str(account['handle']) + "/status/"  + str(recent_user_tweet.id)
        # tweet_node  = twitter_posts.new_node(twitter_posts, str(account['handle'])), { "name" : str(account['name']), "url":tweet_url, "content" : recent_user_tweet.text})
        twitter_posts.insert( str(account['handle']), { "handle" : str(account['handle']), "name" : str(account['name']), "url":tweet_url, "content" : recent_user_tweet.text.encode(UTF_8) })
        handles_in_a_tree.update_node(str(account['handle']), {"handle":str(account['handle']), "name": str(account['name']), "max_id":int(recent_user_tweet.id) }) # update user in twitter_handles
        # print twitter_handles
        signal.alarm(10)   # send signal to process tweet 10 seconds later

#
# post tweet to subreddit
#
def post_thread(reddit_api, tweet):
    global twitter_posts
    print "HIT"
    post = "[{th}] {tp}".format(
                        th = str(tweet['name']),
                        tp = str(tweet['content']) )

    post_url = tweet['url']

    print post, tweet['url'], "\n"
    # subreddit_submission = reddit_api.submission(reddit_api, url=tweet['url'], _data=post)
    twitter_posts.remove(str(tweet['handle']))
    reddit_api.subreddit(subreddit_str).submit(post, url=post_url)


#
# calls the handler get_tweet every interval
#
def signal_get_handler(twitter_api, handles_in_a_tree, interval):
     # check twitter every interval
     handles_in_a_tree.foreach(get_tweet, handles_in_a_tree.psbt._root)
     Timer(interval, signal_get_handler, args=[twitter_api, handles_in_a_tree, interval]).start()


#
# attached to SIGALRM to get called
#
def signal_post_handler(signum, stack):
     twitter_posts.foreach(post_thread, twitter_posts.psbt._root)

def main():
    global handles_in_a_tree
    global handle_list_key, subreddit_str

    # account configuration
    configure_src = open(configuration)
    # twitter creds
    configure_root = json.load(configure_src)
    TWITTER_CONSUMER_KEY = configure_root["TWITTER_CONSUMER_KEY"]
    TWITTER_CONSUMER_SECRET = configure_root["TWITTER_CONSUMER_SECRET"]
    TWITTER_ACCESS_TOKEN = configure_root["TWITTER_ACCESS_TOKEN"]
    TWITTER_ACCESS_KEY = configure_root["TWITTER_ACCESS_KEY"]

    username = configure_root["TWITTER_USER"]
    password = configure_root["TWITTER_PASS"]
    # reddit creds
    REDDIT_CLIENT_ID = configure_root["REDDIT_CLIENT_ID"]
    REDDIT_CLIENT_SECRET = configure_root["REDDIT_CLIENT_SECRET"]
    REDDIT_PASSWORD = configure_root["REDDIT_PASSWORD"]
    REDDIT_USER_AGENT = configure_root["REDDIT_USER_AGENT"]
    REDDIT_USERNAME = configure_root["REDDIT_USERNAME"]
    handle_list_key = configure_root["HANDLE_LIST_KEY"]
    subreddit_str = configure_root["SUBREDDIT"]

    twitter_handles = {}
    # load twitter handles from json
    with open(defaults) as twitter_handles_src:
        t_handles_json_root = json.load(twitter_handles_src)
        handle_list = t_handles_json_root[handle_list_key]
        handle = [item['handle'] for item in handle_list]
        # convert to dictionary to pass to ParallelSBTree
        for i in range(0, len(handle_list)):    # as dicionary
        twitter_handles[str(handle[i])] = {"handle":str(handle[i]), "name": handle_list[i]['name'], "max_id" : handle_list[i]['max_id']}

    twitter_api = setup_twitter_api(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_KEY, username, password)
    reddit_api = setup_reddit_api(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_PASSWORD, REDDIT_USER_AGENT, REDDIT_USERNAME)

    twitter_posts.shared = reddit_api
    handles_in_a_tree = ParallelSBTree(twitter_handles, shared=twitter_api)

    signal_get_handler(twitter_api, handles_in_a_tree, GET_INTERVAL)
    # attach post to  signal.SIGALARM
    signal.signal(signal.SIGALRM, signal_post_handler)


if __name__ == '__main__':
    main()
