#!/usr/bin/env python

"""
Get Twitter access key and secret.
"""

import tweepy

from hasjob import app, init_for

init_for('dev')
auth = tweepy.OAuthHandler(
    app.config['TWITTER_CONSUMER_KEY'], app.config['TWITTER_CONSUMER_SECRET']
)
auth_url = auth.get_authorization_url()
print("Please authorize: " + auth_url)  # noqa: T001
verifier = input('PIN: ').strip()
auth.get_access_token(verifier)
print("TWITTER_ACCESS_KEY = '%s'" % auth.access_token.key)  # noqa: T001
print("TWITTER_ACCESS_SECRET = '%s'" % auth.access_token.secret)  # noqa: T001
