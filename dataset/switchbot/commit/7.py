app = Flask(__name__)

DESCRIPTION = '''
About Switchbot API:
-> https://github.com/OpenWonderLabs/SwitchBotAPI/blob/549798907aeff0504135a3f087affc63657d0207/README.md
'''

API_URL = "https://api.switch-bot.com/v1.0"

PHYSICAL_DEVICE_LIST = [
    'Hub',
    'Hub Plus',
    'Hub Mini',
    'Bot', 'Curtain',
    'Plug',
    'Meter',
    'Motion Sensor',
    'Contact Sensor',
    'Color Bulb',
    'Humidifier',
    'Smart Fan',
    'Strip Light',
    'Plug Mini (US)',
    'Plug Mini (JP)',
    'Lock',
    'Meter Plus (JP)',
    'Meter Plus (US)',
]

def get_token():
    '''
    get token from config.txt
    '''
    with open("token.txt", "r", encoding="utf-8") as in_f:
        token = in_f.read()
        token = str(token).strip()
    return token


OPEN_TOKEN = get_token()
HEADERS = {
    'Authorization': OPEN_TOKEN,
    'Content-Type': 'application/json; charset=utf-8'
}
ENDPOINT_FETCH_STATUS= '/devices/{device_id}/status'
ENDPOINT_SEND_COMMAND= '/devices/{device_id}/command'


def solve_http_status(response: dict) -> dict:
    '''
    solve http status code
    '''
    if type(response) != dict:
        return {"message": "Something was error."}

    status_code = response['statusCode']
    if status_code == 100:
        return response['body']
    elif status_code == 401:
        return {"message": "Unauthorized or Rate Limit Exceeded"}
    else:
        return {"message": "Unknown Error"}


def fetch_device_list() -> json:
    '''
    fetch device list from switch bot api
    '''
    url = f'{API_URL}/devices'
    res = requests.get(url, headers=HEADERS)

    return solve_http_status(res.json())
