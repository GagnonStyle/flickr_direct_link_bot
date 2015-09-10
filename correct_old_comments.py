#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import flickr_api
from flickr_api.api import flickr
import praw
import requests
import time
import os

from config_bot import *
from bot import *


# Setup flickr api
flickr_api.set_keys(api_key = FLICKR_API_KEY, api_secret = FLICKR_API_SECRET)
# Create the Reddit instance
user_agent = ("flickr_direct_link")
reddit = praw.Reddit(user_agent=user_agent)
reddit.login(REDDIT_USERNAME, REDDIT_PASS, disable_warning=True)
subreddits = SUBREDDIT_NAMES

print '====== Started: ' + time.strftime("%H:%M:%S") + '======'
# Have we run this code before? If not, create an empty list
if not os.path.isfile("posts_replied_to.txt"):
    posts_replied_to = []

# If we have run the code before, load the list of posts we have replied to
else:
    # Read the file into a list and remove any empty values
    with open("posts_replied_to.txt", "r") as f:
        posts_replied_to = f.read()
        posts_replied_to = posts_replied_to.split("\n")
        posts_replied_to = filter(None, posts_replied_to)

print 'Looking for comments to remove or fix.'   
for post_id in posts_replied_to:
    post = reddit.get_submission(submission_id=post_id)

    comments = post.comments
    for c in comments:
        if c.author != None and c.author.name == REDDIT_USERNAME and c.body.startswith('###[Direct Photo Link]') and c.replies:
            for reply in c.replies:
                if 'remove' in reply.body.lower() and reply.author.name == post.author.name:
                    print 'Found a link to remove, deleting...'
                    c.delete()
                    break
            break
        #check if previous link still works
        regex = re.match('###\[Direct Photo Link\]\((.*)\)', c.body)
        if regex != None:
            prev_link = regex.group(1)
            response = requests.head(prev_link)
            if response.status_code != 200:
                print 'Broken link, editing to fix...'
                #if the link is broken, edit it with a good link!
                edit_comment(submission=post, comment=c)
print 'Done looking.'
print ''
print '====== Finished: ' + time.strftime("%H:%M:%S") + '======'