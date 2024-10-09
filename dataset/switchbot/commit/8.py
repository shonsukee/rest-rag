BASE_END_POINT = 'https://api.switch-bot.com/v1.0'
devices = requests.get(
    url=BASE_END_POINT + '/devices',
    headers={
        'Authorization': os.environ['SWITCH_BOT_OPEN_TOKEN']
    }
).json()['body']