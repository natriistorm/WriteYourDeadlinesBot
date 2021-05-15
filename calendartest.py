from __future__ import print_function
import datetime
import temp
import googleapiclient
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendar(object):

    def __init__(self, data: list):
        credentials = service_account.Credentials.from_service_account_file(temp.SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
        self.user_data = data
        self.calendarId = data[0]
        if data[1] == 'Add':
            event = self.create_event_dict()
            self.create_event(event)
        elif data[1] == 'Check':
            self.answer = self.get_events_list()

    def create_event_dict(self) -> dict:
        date_start_list = self.user_data[4].split('-')
        start_hour = int(date_start_list[0])
        if start_hour >= 3:
            start_hour = start_hour - 3
            date_start = datetime.datetime(int(date_start_list[3]), int(date_start_list[2]),
                                       int(date_start_list[1]), start_hour).isoformat() + 'Z'
        else:
            start_hour = start_hour + 21
            date_minused = datetime.datetime(int(date_start_list[3]), int(date_start_list[2]),
                                           int(date_start_list[1]), start_hour) - datetime.timedelta(days=1)
            date_start = date_minused.isoformat() + 'Z'
        date_end_list = self.user_data[5].split('-')
        end_hour = int(date_end_list[0])
        if end_hour >= 3:
            end_hour = end_hour - 3
            date_end = datetime.datetime(int(date_end_list[3]), int(date_end_list[2]),
                                           int(date_end_list[1]), end_hour - 3).isoformat() + 'Z'
        else:
            end_hour = end_hour + 21
            date_end = datetime.datetime(int(date_end_list[3]), int(date_end_list[2]),
                                           int(date_end_list[1]), 21 + end_hour) - datetime.timedelta(days=1)
            date_end = date_minused.isoformat() + 'Z'
        event = {
            'summary': self.user_data[2],
            'description': self.user_data[3],
            'start': {'dateTime': date_start},
            'end': {'dateTime': date_end}
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
            answer.append('Нет предстоящих событий.')

        for event in events:
            start = event['start'].get('dateTime',
                                       event['start'].get('date'))

            answer.append((start, event['summary']))
        return answer