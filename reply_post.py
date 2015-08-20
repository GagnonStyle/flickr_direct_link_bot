#!/usr/local/bin/python
import flickr_api
from flickr_api.api import flickr
from imgurpython import ImgurClient
import xml.etree.ElementTree as ET
from urlparse import urlparse
import praw
import pdb
import re
import os
from config_bot import *

# Setup imgur api
imgur_client = ImgurClient(IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET)
# Setup flickr api
flickr_api.set_keys(api_key = FLICKR_API_KEY, api_secret = FLICKR_API_SECRET)
# Create the Reddit instance
user_agent = ("flickr_to_imgur 0.1")
r = praw.Reddit(user_agent=user_agent)
r.login(REDDIT_USERNAME, REDDIT_PASS, disable_warning=True)

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

subreddit = r.get_subreddit('lego')
for submission in subreddit.get_new(limit=7):
    # If we haven't replied to this post before
    if submission.id not in posts_replied_to:

        link_url = urlparse(submission.url)
        if link_url.netloc == 'www.flickr.com':
            print 'Found a new Flickr post!'
            #regex out the photo id, so we can use it in the flickr API
            photo_id = re.search('photos/[^/]+/([0-9]+)', submission.url).group(1)

            # Get all the sizes of the flickr photo
            print 'Getting image from Flickr...'
            sizes_xml = flickr.photos.getSizes(photo_id = photo_id)
            # Last == Biggest, (But sometimes biggest is too big for imgur)
            sizes = ET.fromstring(sizes_xml).findall('sizes/size')
            if sizes[-1].get('label') == 'Original':
                biggest_size = sizes[-2]
            else:
                biggest_size = sizes[-1]
            image_url = biggest_size.get('source')

            print 'Uploading to Imgur...'
            uploaded = imgur_client.upload_from_url(image_url, config=None, anon=True)
            print 'Uploaded!'

            print 'Posting Comment...'
            submission.add_comment('[Imgur Mirror](' + uploaded['link'] + ')')
            posts_replied_to.append(submission.id)
            print 'Comment Posted!'

# Write our updated list back to the file
with open("posts_replied_to.txt", "w") as f:
    for post_id in posts_replied_to:
        f.write(post_id + "\n")