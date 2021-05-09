from __future__ import print_function
import datetime
import time
import config
import googleapiclient
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendar(object):
    calendarId = 'c_4id5047dn2h8j29rbjvagkls5o@group.calendar.google.com'

    def __init__(self, data: list):
        credentials = service_account.Credentials.from_service_account_file(config.SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
        self.user_data = data
        if data[0] == 'Add':
            event = self.create_event_dict()
            self.create_event(event)
        elif data[0] == 'Check':
            self.answer = self.get_events_list()

    def create_event_dict(self) -> dict:
        date_start_list = self.user_data[3].split('-')
        date_start_time = datetime.time(0, 0, 0).isoformat()
        date_start = datetime.datetime(int(date_start_list[2]), int(date_start_list[1]),
                                       int(date_start_list[0])).isoformat()
        event = {
            'summary': self.user_data[1],
            'description': self.user_data[2],
            'start': {'dateTime': datetime.datetime.fromtimestamp(round(time.time()) - 2000).isoformat() + 'Z'},
            'end': {'dateTime': datetime.datetime.fromtimestamp(round(time.time()) + +7000).isoformat() + 'Z'}
        }
        return event

    def create_event(self, new_event):
        self.service.events().insert(calendarId=self.calendarId, body=new_event).execute()

    def get_events_list(self) -> str:
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = self.service.events().list(calendarId=self.calendarId, timeMin=now, maxResults=10,
                                                   singleEvents=True, orderBy='startTime').execute()

        events = events_result.get('items', [])
        answer = []
        if not events:
            answer.append('No upcoming events found.')

        for event in events:
            start = event['start'].get('dateTime',
                                       event['start'].get('date'))

            answer.append((start, event['summary']))
        return answer
