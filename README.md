#Flickr Direct Link Bot
A Reddit bot that posts direct photo links in the comments section of Flickr link posts.

To use:
* Create your own config_bot.py from config_boy.py.example. (You will need to sign up for a Flickr API key in order to do this.)
* You'll have to specify the subreddit you want to post to in config_bot.py as well.
* Set the bot running on some regular interval, and you're good to go! (I have it running every 5 minutes using cron/crontab, but there may be better solutions or more efficient time intervals.)
