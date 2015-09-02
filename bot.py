#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import praw
import re
import urllib
from urlparse import urlparse
import xml.etree.ElementTree as ET
from flickr_api.api import flickr

def new_comment(submission):
    parsed_url = urlparse(submission.url)
    real_url = get_real_link_url(parsed_url)
    #regex out the photo id, so we can use it in the flickr API
    if re.search('photos/[^/]+/([0-9]+)', real_url) != None:
        photo_id = re.search('photos/[^/]+/([0-9]+)', real_url).group(1)

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
            try:
                submission.add_comment('###[Direct Photo Link](' + image_url + ')\n' +
                                       '*****\n' +
                                       '^^Are you OP? Would you like this link removed?\n' +
                                       '^^Just comment \'remove\' and the bot will trash it the next time it runs!\n' +
                                       '^^This bot uses the flickr API to get a direct link to the posted photo.\n' +
                                       '^^It does not rehost or mirror the image in any way. Check out the source code on [GitHub](https://github.com/GagnonStyle/flickr_to_imgur)')
                print 'Comment Posted!'
                return True
            except praw.errors.RateLimitExceeded, e:
                print e
        else:
            print 'Can\'t rehost this photo! (copyright stuff...)'
    else:
        print 'The post was an album, too bad!'
    return False
def edit_comment(submission, comment):
    parsed_url = urlparse(submission.url)
    real_url = get_real_link_url(parsed_url)
    #regex out the photo id, so we can use it in the flickr API
    if re.search('photos/[^/]+/([0-9]+)', real_url) != None:
        photo_id = re.search('photos/[^/]+/([0-9]+)', real_url).group(1)

        # Get all the sizes of the flickr photo
        print 'Getting image from Flickr...'
        info = flickr.photos.getInfo(photo_id = photo_id)
        if ET.fromstring(info).findall('photo/usage')[0].get('candownload') == '1':
            sizes_xml = flickr.photos.getSizes(photo_id = photo_id)
            # Last == Biggest
            sizes = ET.fromstring(sizes_xml).findall('sizes/size')
            biggest_size = sizes[-1]

            image_url = biggest_size.get('source')

            print 'Editing Comment...'
            try:
                comment.edit('###[Direct Photo Link](' + image_url + ')\n' +
                             '*****\n' +
                             '^^Are you OP? Would you like this link removed?\n' +
                             '^^Just comment \'remove\' and the bot will trash it the next time it runs!\n' +
                             '^^This bot uses the flickr API to get a direct link to the posted photo.\n' +
                             '^^It does not rehost or mirror the image in any way. Check out the source code on [GitHub](https://github.com/GagnonStyle/flickr_to_imgur)')
                print 'Comment Edited!'
                return True
            except praw.errors.RateLimitExceeded, e:
                print e
        else:
            print 'Can\'t rehost this photo! (copyright stuff...)'
    else:
        print 'The post was an album, too bad!'
    return False
def get_real_link_url(parsed_url):
    #deal with shortened urls
    if parsed_url.netloc == 'flic.kr':
        return urllib.urlopen(parsed_url.geturl()).url
    else:
        return parsed_url.geturl()