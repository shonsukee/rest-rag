switchbot_host = 'https://api.switch-bot.com/v1.0'

class SwitchBotClient:
    def __init__(self, token: str):
        self.session = requests.Session()
        self.session.headers['Authorization'] = token
