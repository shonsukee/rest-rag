
class SwitchBotAPIClient(object):
    """
    For Using SwitchBot via official API.
    Please see https://github.com/OpenWonderLabs/SwitchBotAPI for details.
    """
    def __init__(self, token):
        self._host_domain = "https://api.switch-bot.com/v1.0/"
        self.token = token
        self.device_list = None
        self.infrared_remote_list = None
        self.scene_list = None
        self.device_name_id = {}
        self.scene_name_id = {}
        self.update_device_list()
        self.update_scene_list()


    def request(self, method='GET', devices_or_scenes='devices', service_id='', service='', json_body=None):
        """
        Execute HTTP request
        """
        if devices_or_scenes not in ['devices', 'scenes']:
            raise ValueError('Please set devices_or_scenes variable devices or scenes')

        url = os.path.join(self._host_domain, devices_or_scenes, service_id, service)

        if method == 'GET':
            response = requests.get(
                url,
                headers={'Authorization': self.token}
            )
        elif method == 'POST':
            response = requests.post(
                url,
                json_body,
                headers={
                    'Content-Type': 'application/json; charset=utf8',
                    'Authorization': self.token
            })
        else:
            raise ValueError('Got unexpected http request method. Please use GET or POST.')

        response_json = response.json()

        # Catch the HTTP 4XX, 5XX error
        try:
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            if response.status_code == 422:
                raise InvalidRequestError()
            elif response.status_code == 429:
                raise ExceededRequestError()
            else:
                raise e
        else:
            if response_json['statusCode'] == 100:
                return response_json
            elif response_json['statusCode'] == 151:
                raise DeviceTypeError()
            elif response_json['statusCode'] == 152:
                raise DeviceNotFoundError()
            elif response_json['statusCode'] == 160:
                raise CommandNotSupportedError()
            elif response_json['statusCode'] == 161:
                raise DeviceOfflineError()
            elif response_json['statusCode'] == 171:
                raise HubDeviceOfflineError()
            elif response_json['statusCode'] == 190:
                raise DeviceInternalError()
            else:
                raise ValueError("Got unknown status code : " + str(response_json['statusCode']))
