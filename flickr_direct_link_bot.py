#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import flickr_api
from flickr_api.api import flickr
import xml.etree.ElementTree as ET
from urlparse import urlparse
import praw
import pdb
import re
import os
from config_bot import *

# Setup flickr api
flickr_api.set_keys(api_key = FLICKR_API_KEY, api_secret = FLICKR_API_SECRET)
# Create the Reddit instance
user_agent = ("flickr_to_imgur 0.1")
r = praw.Reddit(user_agent=user_agent)
r.login(REDDIT_USERNAME, REDDIT_PASS, disable_warning=True)
subreddit = r.get_subreddit(SUBREDDIT_NAME)

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

for post_id in posts_replied_to:
    post = r.get_submission(submission_id=post_id)
    comments = post.comments
    for c in comments:
        if c.author != None and c.author.name == 'FlickrToImgurBot' and c.body.startswith('###[Direct Photo Link]') and c.replies:
            for reply in c.replies:
                if 'remove' in reply.body.lower() and reply.author.name == post.author.name:
                    print 'Found a link to remove, deleting...'
                    c.delete()
                    break


for submission in subreddit.get_new(limit=10):
    # If we haven't replied to this post before
    if submission.id not in posts_replied_to:

        link_url = urlparse(submission.url)
        if link_url.netloc == 'www.flickr.com':
            print 'Found a new Flickr post!'
            #regex out the photo id, so we can use it in the flickr API
            photo_id = re.search('photos/[^/]+/([0-9]+)', submission.url).group(1)

            # Get all the sizes of the flickr photo
            print 'Getting image from Flickr...'
            info = flickr.photos.getInfo(photo_id = photo_id)
            if ET.fromstring(info).findall('photo/usage')[0].get('candownload') == '1':
                sizes_xml = flickr.photos.getSizes(photo_id = photo_id)
                # Last == Biggest
                sizes = ET.fromstring(sizes_xml).findall('sizes/size')
                biggest_size = sizes[-1]

                image_url = biggest_size.get('source')

                print 'Posting Comment...'

                submission.add_comment('###[Direct Photo Link](' + image_url + ')\n' +
                                       '*****\n' +
                                       '^^Are you OP? Would you like this link removed?\n' +
                                       '^^Just comment \'remove\' and the bot will trash it the next time it runs!\n' +
                                       '^^This bot uses the flickr API to get a direct link to the posted photo.\n' +
                                       '^^It does not rehost or mirror the image in any way. Check out the source code on [GitHub](https://github.com/GagnonStyle/flickr_to_imgur)')
                posts_replied_to.append(submission.id)
                print 'Comment Posted!'
            else:
                print 'Can\'t rehost this photo! (copyright stuff...)'

# Write our updated list back to the file
with open("posts_replied_to.txt", "w") as f:
    for post_id in posts_replied_to:
        f.write(post_id + "\n")