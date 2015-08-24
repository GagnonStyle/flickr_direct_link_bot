#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import flickr_api
from flickr_api.api import flickr
from urlparse import urlparse
import praw
import requests
import urllib
import pdb
import os
import time
from config_bot import *
from bot import *

print '======' + time.strftime("%H:%M:%S") + '======'
# Setup flickr api
flickr_api.set_keys(api_key = FLICKR_API_KEY, api_secret = FLICKR_API_SECRET)
# Create the Reddit instance
user_agent = ("flickr_direct_link")
reddit = praw.Reddit(user_agent=user_agent)
reddit.login(REDDIT_USERNAME, REDDIT_PASS, disable_warning=True)
subreddits = SUBREDDIT_NAMES

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
for sub_name in subreddits:
    print 'Looking for new flickr posts in /r/' + sub_name
    sub = reddit.get_subreddit(sub_name)
    for submission in sub.get_new(limit=7):
        # If we haven't replied to this post before
        if submission.id not in posts_replied_to:

            parsed_url = urlparse(submission.url)
            if parsed_url.netloc == 'www.flickr.com' or parsed_url.netloc =='flic.kr':

                print 'Found a new Flickr post!'

                result = new_comment(submission=submission)
                if result:
                    posts_replied_to.append(submission.id)

print 'Done!'
# Write our updated list back to the file
with open("posts_replied_to.txt", "w") as f:
    for post_id in posts_replied_to:
        f.write(post_id + "\n")
print '==========='
