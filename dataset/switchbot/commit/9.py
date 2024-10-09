class SwitchBotAPI:
    
    base_url = "https://api.switch-bot.com"
    token = False
    version = "v1.0"
    
    def __init__(self, token=False) -> None:
        if token:
            self.token = token
        else:
            self.token = lifestream.config.get("switchbot", "token")

    def call(self, method, callname, data={}):
        URL = '{}/{}/{}'.format(self.base_url, self.version, callname)
        
        headers = {
            'authorization' : self.token
        }

        if method == 'post':
            headers['content-type'] = 'application/json; charset=utf8'
            r = requests.post(URL, data=data, headers=headers)
        elif method == 'get':
            r = requests.get(URL, params=data, headers=headers)

        return r.json()
