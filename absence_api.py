from dateutil import parser
from requests_hawk import HawkAuth
import json

import requests
import datetime
import time


class AbsenceAPI(object):

    def __init__(self, absence_id, absence_key):
        self.absence_id = absence_id
        self.absence_key = absence_key
        self.api_url = "https://app.absence.io/api/v2/{}"
        self.hawk_auth = HawkAuth(id=absence_id, key=absence_key)

    def __request(self, url, payload):
        try:
            r = requests.post(url, auth=self.hawk_auth, json=payload)
            r.raise_for_status()
            return r
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    def get_all_absences(self):
        today = datetime.date.today()
        payload = {
            "skip": 0,
            "limit": 100,
            "filter": {
                "start": {
                    "$gte": f"{today.year}-01-01"
                },
                "assignedToId": self.absence_id
            },
            "relations": [
                "assignedToId",
                "reasonId",
                "approverId"
            ]
        }

        json_response = self.__request(self.api_url.format("absences"), payload).json()
        # print(f"Status Code: {r.status_code}, Response: {json.dumps(json_response, indent=2)}")

        absences = []
        for data in json_response["data"]:
            start = parser.parse(data['startDateTime'])
            end = parser.parse(data['endDateTime'])

            date_range = [start + datetime.timedelta(days=x) for x in range((end - start).days)]
            for date in date_range:
                absences.append(date)

        return absences

    def get_timespans(self, date):
        payload = {
            "skip": 0,
            "limit": 100,
            "filter": {
                "userId": self.absence_id,
                "start": {
                    "$gte": date
                }
            }
        }

        json_response = self.__request(self.api_url.format("timespans"), payload).json()
        # print(f"Status Code: {r.status_code}, Response: {json.dumps(json_response, indent=2)}")

        timespans = []
        for data in json_response["data"]:
            start = parser.parse(data['startInTimezone'])
            if data['type'] == 'work':
                timespans.append(start)

        return list(set(timespans))

    def post_timespan(self, start_date, end_date, type):
        payload = {
            "userId": self.absence_id,
            "start": start_date,
            "end": end_date,
            "timezoneName": time.strftime('%Z'),
            "timezone": time.strftime('%z'),
            "type": type,
            "source": {
                "sourceType": "browser",
                "sourceId": "manual"
            }
        }

        r = self.__request(self.api_url.format("timespans/create"), payload)
        print(f"Status Code: {r.status_code}, Response: {json.dumps(r.json(), indent=2)}")
