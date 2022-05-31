from app.module_calendar.quickstart import get_calendar_service
from geopy.geocoders import Nominatim


def main():
    service = get_calendar_service()

    event = {
    'summary': 'Pruebitax2 Dia',
    'location': '800 Howard St., San Francisco, CA 94103',
    'description': 'Pues una prueba',
    'start': {
        'dateTime': '2022-05-10T09:00:00',  
        'timeZone': 'Europe/Madrid',
    },
    'end': {
        'dateTime': '2022-05-10T10:00:00',
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


    """'attendees': [
        {'email': 'lpage@example.com'},
        {'email': 'sbrin@example.com'},
    ],"""
    event = service.events().insert(calendarId='primary', body=event).execute()
    print ('Event created: %s' % (event.get('htmlLink')))



    print("created event")
    print("id: ", event['id'])
    print("summary: ", event['summary'])
    print("starts at: ", event['start']['dateTime'])
    print("ends at: ", event['end']['dateTime'])

if __name__ == '__main__':
   main()

def eliminarEventoID(tokenUser, eventID):
    service = get_calendar_service(tokenUser)
    service.events().delete(calendarId='primary', eventId= eventID ).execute()

def eliminarEventoTitle(tokenUser, title):
    service = get_calendar_service(tokenUser)
    events = buscarEventoTitle(tokenUser, title)
    for event in events['items']:
        eliminarEventoID(tokenUser, event['id'])
    if events['items'] == []:
        print("No hay eventos con este titulo")


def buscarEventoTitle(tokenUser, title):
    service = get_calendar_service(tokenUser)
    
    events = service.events().list(calendarId='primary', singleEvents=True, q=title).execute()
    for event in events['items']:
        print( event['summary'])
        print( event['id'])
        print( event['location'])
        print(event['start']['dateTime'])
        print(event['end']['dateTime'])
    if events['items'] == []:
        print("No hay eventos con este titulo")
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


    """'attendees': [
        {'email': 'lpage@example.com'},
        {'email': 'sbrin@example.com'},
    ],"""
    event = service.events().insert(calendarId='primary', body=event).execute()
    print ('Event created: %s' % (event.get('htmlLink')))



    print("created event")
    print("id: ", event['id'])
    print("summary: ", event['summary'])
    print("starts at: ", event['start']['dateTime'])
    print("ends at: ", event['end']['dateTime'])


def obtenerLocation(latitude, longitude):
    # calling the nominatim tool
    geoLoc = Nominatim(user_agent="GetLoc")
    # passing the coordinates
    locname = geoLoc.reverse(str(latitude)+","+ str(longitude))
    print (locname)
    return locname

def editarEventoTitle(tokenUser, oldTitle, newTitle):
    service = get_calendar_service(tokenUser)
    events = buscarEventoTitle(tokenUser, oldTitle)
    for event in events['items']:
        #modificar aqui cada evento
        event['summary'] = newTitle
        updated_event = service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
        print( updated_event['updated'])

def editarEventoDate(tokenUser,title, dateTimeStart, dateTimeEnd):
    service = get_calendar_service(tokenUser)
    events = buscarEventoTitle(tokenUser, title)
    for event in events['items']:
        #modificar aqui cada evento
        event['start']['dateTime'] = dateTimeStart
        event['end']['dateTime'] = dateTimeEnd
        updated_event = service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
        print( updated_event['updated'])

def editarEventoDesciption(tokenUser, title, description):
    service = get_calendar_service(tokenUser)
    events = buscarEventoTitle(tokenUser, title)
    for event in events['items']:
        #modificar aqui cada evento
        event['description'] = description
        updated_event = service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
        print( updated_event['updated'])
