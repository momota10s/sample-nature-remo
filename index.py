import requests
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials


class NatureRemoClient(object):
    def __init__(self, base_url=None):
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = "https://api.nature.global"
        token = "your-token"
        if not token:
            raise Exception('Please set your API token to REMO_TOKEN')
        self.headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer ' + token
        }

    def call_api(self, url, method='get', params=None):
        req_method = getattr(requests, method)
        try:
            res = req_method(
                self.base_url + url,
                headers=self.headers,
                params=params
            )
            return res.json()
        except Exception as e:
            raise Exception('Failed to call API: %s' % str(e))

    def get_devices(self):
        url = '/1/devices'
        return self.call_api(url)

    def get_device(self, device_name=None, device_id=None):
        devices = self.get_devices()
        if device_id:
            device = [d for d in devices if d['id'] == device_id]
            return device[0]
        elif device_name:
            device = [d for d in devices if d['name'] == device_name]
            return device[0]
        else:
            return devices[0]

    def get_newest_events(self, device_name=None, event_name=None):
        if device_name:
            device = self.get_device(device_name=device_name)
        else:
            device = self.get_device()
        if event_name:
            return device['newest_events'][event_name]
        else:
            return device['newest_events']


class SpreadSheet(object):
    def __init__(self):
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        credential = {
            "type": "service_account",
            "project_id": "",
            "private_key_id": "",
            "private_key": "your-private-key",
            "client_email": "",
            "client_id": "",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": ""
        }
        cred = ServiceAccountCredentials.from_json_keyfile_dict(credential, scope)
        self.gs = gspread.authorize(cred)

    def open_sheet(self):
        self.sheet = self.gs.open_by_key("your-key").sheet1

    def get_col_length(self, row=1):
        return len(self.sheet.col_values(row))

    def update_column(self, line, values):
        cells = self.sheet.range(line, 1, line, len(values))
        for i in range(len(cells)):
            cells[i].value = values[i]
            self.sheet.update_cells(cells)


def run_function(event, context):
    gs = SpreadSheet()
    gs.open_sheet()
    last_line = gs.get_col_length()
    if last_line == 0:
        header = [
            'timestamp',
            'timestamp_unix',
            'temperature',
            'temperature_created',
            'humidity',
            'humidity_created',
            'illumination',
            'illumination_created',
            'motion',
            'motion_created'
        ]
        gs.update_column(1, header)
        last_line += 1

    now = datetime.datetime.now(datetime.timezone.utc)
    client = NatureRemoClient()
    events = client.get_newest_events()
    now_iso = now.isoformat()

    values = [
        now_iso,
        int(now.timestamp()),
        events['te']['val'],
        events['te']['created_at'],
        events['hu']['val'],
        events['hu']['created_at'],
        events['il']['val'],
        events['il']['created_at'],
        events['mo']['val'],
        events['mo']['created_at']
    ]
    gs.update_column(last_line + 1, values)
