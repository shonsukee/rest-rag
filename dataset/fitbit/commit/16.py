"""Client to work with Fitbit API"""

__author__ = 'bird@codeminders.com (Alexander Sova)'

import logging

import util

class FitbitAPI:
  """Fitbit API Client implementation"""

  def __init__(self, userid):
    self.userid = userid
    self.fitbit_service = util.create_fitbit_service_for_user(userid)

  def is_ready(self):
    return self.fitbit_service != None

  def get_subscriptions(self):
    """Returns list of all 'm-distance' subscriptions for given user"""
   
    r = self.fitbit_service.get('http://api.fitbit.com/1/user/-/apiSubscriptions.json', header_auth=True)
    if r.status_code == 200:
      subs = r.json()['apiSubscriptions']
      return [s for s in subs if s['subscriberId'] == 'm-distance']

  def create_subscription(self):
    """Creates new Fitbit subscription for for given user"""

    self.clear_subscriptions()

    # creating new subscription
    r = self.fitbit_service.post('http://api.fitbit.com/1/user/-/apiSubscriptions/%s.json' % self.userid, data={}, header_auth=True)
    logging.info('Adding new subscription for user %s. The code: %s Message: %s', self.userid, r.status_code, r.text)

  def clear_subscriptions(self):
    """Deletes all Fitbit subscriptions for for given user"""

    subs = self.get_subscriptions()
    for s in subs:
      self.delete_subscription(s['subscriptionId'])

  def delete_subscription(self, subscriptionId):
    """Deletes Fitbit subscription for for given user"""

    r = self.fitbit_service.delete('http://api.fitbit.com/1/user/-/apiSubscriptions/%s.json' % subscriptionId, data={}, header_auth=True)
    logging.info('Deleting subscription. Id: %s. The code: %s Message: %s', subscriptionId, r.status_code, r.text)

  def get_user_profile(self):
    """Returns user profile information"""
    r = self.fitbit_service.get('http://api.fitbit.com/1/user/-/profile.json', header_auth=True)
    logging.debug('Getting user profile. %s %s', r.status_code, r.text)
    if r.status_code != 200:
      return None
    return r.json()

  def get_activities_info(self, date):
    """Returns activities info for given date"""
    r = self.fitbit_service.get('http://api.fitbit.com/1/user/-/activities/date/%s.json' % date, header_auth=True)
    logging.debug('Getting activities. %s %s', r.status_code, r.text)
    if r.status_code != 200:
      return None
    return r.json()

  def get_activities_goals(self):
    """Returns daily activity goals info"""
    r = self.fitbit_service.get('http://api.fitbit.com/1/user/-/activities/goals/daily.json', header_auth=True)
    logging.debug('Getting Daily Activity Goals. %s %s', r.status_code, r.text)
    if r.status_code != 200:
      return None
    return r.json()

  def get_devices_info(self):
    """Returns devices info"""
    r = self.fitbit_service.get('http://api.fitbit.com/1/user/-/devices.json', header_auth=True)
    logging.debug('Getting Devices Info. %s %s', r.status_code, r.text)
    if r.status_code != 200:
      return None
    return r.json()