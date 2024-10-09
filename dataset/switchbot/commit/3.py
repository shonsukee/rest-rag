class call:
    def __init__(self, payload):
        item = payload['data']
        text = item['text']
        rtmclient = payload['rtm_client']
        webclient = payload['web_client']
        channel = item['channel']
        ts = item.get('ts')

        if item.get('bot_id', None) is None:
            module = __name__.replace('modules.', '')
            options = rtmclient.options[module]
            if isinstance(options, dict):
                on = options['on']
                off = options['off']
                ouser = options['user']
                user_id = item.get('user')
                username = rtmclient.caches.user_ids.get(user_id)
                if (text == on or text == off) and ouser == username:
                    token = options['token']
                    device = options['device']
                    commands = {
                        on: 'turnOn',
                        off: 'turnOff',
                    }
                    command = commands[text]

                    # https://github.com/OpenWonderLabs/SwitchBotAPI#send-device-control-commands
                    try:
                        requests.post('https://api.switch-bot.com/v1.0/devices/{}/commands'.format(device),
                                      headers={'Authorization': token},
                                      json={
                                          'command': command,
                                          'parameter': 'default',
                                          'commandType': 'command',
                                      },
                                      timeout=10)
                        webclient.reactions_add(
                            channel=channel,
                            name='ok',
                            timestamp=ts,
                        )
                    except Exception:
                        webclient.reactions_add(
                            channel=channel,
                            name='ng',
                            timestamp=ts,
                        )