from __future__ import print_function

import datetime
import os.path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account


#https://developers.google.com/identity/protocols/oauth2/service-account
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']



def get_calendar_service(tokenUser):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('app/module_calendar/token.json'):
       with open('app/module_calendar/token.json', 'r+') as token:
           data = json.load(token)
           data['token'] = tokenUser
           token.seek(0)
           json.dump(data, token, indent=4)
           token.truncate()
       creds = Credentials.from_authorized_user_file('app/module_calendar/token.json', SCOPES)
       print(creds.to_json()[0])
       

    """
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(  #secretfile
                'app/module_calendar/hola.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        #we delegated credentials for user of the app       
        #creds = service_account.Credentials.from_service_account_file(
        #    'app/module_calendar/SocialOutServicex2.json', scopes=SCOPES)
        #delegated_credentials = creds.with_subject('francesc.holly@estudiantat.upc.edu') """
    service = build('calendar', 'v3', credentials=creds)

        
    """try:
            service = build('calendar', 'v3', credentials=creds)

            # Call the Calendar API
            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            print('Getting the upcoming 10 events')
            events_result = service.events().list(calendarId='primary', timeMin=now,
                                                maxResults=10, singleEvents=True,
                                                orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                print('No upcoming events found.')
                return

            # Prints the start and name of the next 10 events
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(start, event['summary'])

        except HttpError as error:
            print('An error occurred: %s' % error) """
    return service

    """
    if __name__ == '__main__':
        main() """