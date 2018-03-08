from __future__ import print_function
import httplib2
import os
import datetime

from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient import discovery
from dateutil.parser import parse

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json' # update if you decide rename the file
APPLICATION_NAME = 'Google Calendar Event Counter'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def callForEvents(start, end, max = 100):
    """Sorts through events from start to end parameters

    The default maximum is set to 100, feel free to overwrite this if you want more or less events.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = start.isoformat() + 'Z' # 'Z' indicates UTC time
    up_to = end.isoformat() + 'Z' # 'Z' indicates UTC time

    return service.events().list(
        calendarId='primary', timeMin=now, timeMax = up_to, maxResults=max, singleEvents=True,
        orderBy='startTime').execute()

def sortEvents(start, end, event_to_count):
    """Sorts through events from start to end parameters

    """
    eventsResult = getEvents(start, end)
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    count = 0
    for event in events:
        title = event['summary'].lower()
        start = event['start'].get('dateTime', event['start'].get('time'))
        end =  event['end'].get('dateTime', event['end'].get('time'))
        if (end is not None):
            end_obj = parse(end)
            start_obj = parse(start)
            duration = end_obj-start_obj
            secs = duration.total_seconds()
            hours = secs/60/60
        if 'event_to_count' in title:
            count+=hours
    print ('--------------------------------------------')
    print ('hours spent on ', event_to_count, ': ', count)

def range_option(m1, d1, m2, d2, pacific_time=True):
    """ Counts events in the specified month-date-month-date.
    Hardcoded to 2018 as the year, may add option to add year paramater
    Default to pacific time, may add option for other time zones

    """
    date_min = datetime.datetime(2018, m1, d1)
    date_max = datetime.datetime(2018, m2, d2)
    if (pacific_time) : 
        offset = datetime.timedelta(hours = 8)
        date_min += offset
        date_max += offset
    sortEvents(date_min, date_max)

def default():
    days = input("How many days from now do you want to check? (excludes the nth day) ")
    print ('Getting the upcoming', days, 'days')
    now = datetime.datetime.utcnow()
    up_to = now + datetime.timedelta(days=days)
    sortEvents(now, up_to)

def getopts(argv):
    opts = {} 
    while argv:  
        toSlice = 1
        if (argv[0] == '-mdmd'): 
            opts[argv[0]] = [int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4])] 
            toSlice = 4 
        elif (argv[0] == '-p'):
            opts[argv[0]] = True
        argv = argv[toSlice:]
    return opts

if __name__ == '__main__':
    from sys import argv
    myargs = getopts(argv)
    if '-mdmd' in myargs:  
        param = myargs['-mdmd']
        if '-p' in myargs:
            range_option(param[0],param[1],param[2],param[3], True)   
        else:
            range_option(param[0],param[1],param[2],param[3])    
    else:
        default()
