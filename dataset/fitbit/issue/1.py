import logging
import json
import fitbit

class Helper(object):
	"""Helper methods to hide trivial methods"""
	def __init__(self, fitbitCredsFile, googleCredsFile):
		""" Intialize a helper object.
		fitbitCredsFile -- Fitbit credentials file
		googleCredsFile -- Google Fits credentials file
		"""
		self.fitbitCredsFile = fitbitCredsFile
		self.googleCredsFile = googleCredsFile

	def GetFitbitClient(self):
		"""Returns an authenticated fitbit client object"""
		logging.debug("Creating Fitbit client")
		credentials = json.load(open(self.fitbitCredsFile))  
		client = fitbit.Fitbit(**credentials)
		logging.debug("Fitbit client created")
		return client
