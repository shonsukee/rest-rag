def _headers(self):
	version = AppConstants.VERSION
	return {
		"content-type": "application/json",
		"authorization": self.token,
		"user-agent": f"switchbot-client/{version}",
	}