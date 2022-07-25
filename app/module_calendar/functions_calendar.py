import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from geopy.geocoders import Nominatim

def get_calendar_service(tokenUser):
    creds = Credentials.from_authorized_user_info({
        "token": tokenUser,
        "refresh_token": "",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": os.getenv('GOOGLE_CLIENT_ID'),
        "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
        "scopes": [
            "https://www.googleapis.com/auth/calendar"
        ],
        "expiry": "2023-05-29T23:19:42.576951Z"
    }, ['https://www.googleapis.com/auth/calendar'])
    service = build('calendar', 'v3', credentials=creds)
    return service

def eliminarEventoID(tokenUser, eventID):
    service = get_calendar_service(tokenUser)
    service.events().delete(calendarId='primary', eventId= eventID ).execute()

def eliminarEventoTitle(tokenUser, title):
    events = buscarEventoTitle(tokenUser, title)
    for event in events['items']:
        eliminarEventoID(tokenUser, event['id'])
    if events['items'] == []:
        raise Exception(f"No hay eventos con titulo {title}")


def buscarEventoTitle(tokenUser, title):
    service = get_calendar_service(tokenUser)
    events = service.events().list(calendarId='primary', singleEvents=True, q=title).execute()
    if events['items'] == []:
        raise Exception(f"No hay eventos con titulo {title}")
    return events


def crearEvento(tokenUser, title, description, latitude, longitude, startDateTime, endDateTime):
    service = get_calendar_service(tokenUser)
    location = obtenerLocation(latitude, longitude)
    event = {
        'summary': title,
        'location': str(location),
        'description': description,
        'start': {
            'dateTime': startDateTime,  
            'timeZone': 'Europe/Madrid',
        },
        'end': {
            'dateTime': endDateTime,
            'timeZone': 'Europe/Madrid',
        },
        
        
        'reminders': {
            'useDefault': False,
            'overrides': [
            {'method': 'email', 'minutes': 24 * 60},
            {'method': 'popup', 'minutes': 10},
            ],
        },
    }
    
    event = service.events().insert(calendarId='primary', body=event).execute()


def obtenerLocation(latitude, longitude):
    # calling the nominatim tool
    geoLoc = Nominatim(user_agent="GetLoc")
    # passing the coordinates
    locname = geoLoc.reverse(str(latitude)+","+ str(longitude))
    return locname

def editarEventoTitle(tokenUser, oldTitle, newTitle):
    service = get_calendar_service(tokenUser)
    events = buscarEventoTitle(tokenUser, oldTitle)
    for event in events['items']:
        #modificar aqui cada evento
        event['summary'] = newTitle
        service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()

def editarEventoDate(tokenUser,title, dateTimeStart, dateTimeEnd):
    service = get_calendar_service(tokenUser)
    events = buscarEventoTitle(tokenUser, title)
    for event in events['items']:
        #modificar aqui cada evento
        event['start']['dateTime'] = dateTimeStart
        event['end']['dateTime'] = dateTimeEnd
        service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()

def editarEventoDesciption(tokenUser, title, description):
    service = get_calendar_service(tokenUser)
    events = buscarEventoTitle(tokenUser, title)
    for event in events['items']:
        #modificar aqui cada evento
        event['description'] = description
        service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
