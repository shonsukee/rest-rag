"""Utility functions."""

import logging

from rauth.service import OAuth1Service

from oauth2client.anyjson import simplejson

def create_fitbit_oauth_service():
  #TODO: cache in memcache, like lib/oauth2client/clientsecrets.py
  try:
    fp = file('fitbit_secrets.json', 'r')
    try:
      json = simplejson.load(fp)
    finally:
      fp.close()
  except IOError:
    logging.error('Cannot find Fitbit service info')
    return None

  return OAuth1Service(
    consumer_key=json['consumer_key'],
    consumer_secret=json['consumer_secret'],
    name='fitbit',
    request_token_url='http://api.fitbit.com/oauth/request_token',
    authorize_url='http://www.fitbit.com/oauth/authorize',
    access_token_url='http://api.fitbit.com/oauth/access_token',
    base_url='http://api.fitbit.com')
