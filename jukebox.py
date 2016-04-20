from __future__ import print_function
import requests
import xml.etree.ElementTree as ET

server = ''
u = ''
p = ''
s = ''
t = ''
v = '1.13.0'
app = ''

payload = {'u': u, 's':s, 't':t, 'v':v, 'c':app}

def clear():
    global payload
    payload['action']='clear'
    r = requests.get(server + '/rest/jukeboxControl.view', params=payload)

def getrandom():
    global payload
    r = requests.get(server + '/rest/getRandomSongs.view', params=payload)
    resp = r.text

    root_element = ET.fromstring(resp)
    
    songs = []
    
    for child in root_element:
        for song in child:
            print(song.get('id'), song.get('path'))
            songs.append(song.get('id'))
    return songs

def addrandom(songs):
    global payload
    payload['action']='add'
    
    for song in songs:
        payload['id']=song
        r = requests.get(server + '/rest/jukeboxControl.view', params=payload)
        del payload['id']

def getplaylist():
    payload['action']='get'
    r = requests.get(server + '/rest/jukeboxControl.view', params=payload)

def getstatus():
    payload['action']='status'
    r = requests.get(server + '/rest/jukeboxControl.view', params=payload)

def start():
    payload['action']='start'
    r = requests.get(server + '/rest/jukeboxControl.view', params=payload)

def nowplaying():
    # get playlist
    payload['action']='get'
    r = requests.get(server + '/rest/jukeboxControl.view', params=payload)

    resp = r.text
    root_element = ET.fromstring(resp)

    songs = []

    for child in root_element:
        for song in child:
            songs.append({
                'id': song.get('id'),
                'artist': song.get('artist'),
                'album': song.get('album'),
                'title': song.get('title')})

    #get offset
    payload['action']='status'
    r = requests.get(server + '/rest/jukeboxControl.view', params=payload)

    root_element = ET.fromstring(r.text)

    current_index = int(root_element[0].get('currentIndex'))

    return songs[current_index]

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """

    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "PlayHotJams":
        return play_jams()
    elif intent_name == "WhatsPlaying":
        return whatsplaying()
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Functions that control the skill's behavior ------------------
def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to ze jukebox"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Welcome to ze jukebox"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thanks. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def play_jams():
    """
    """
    session_attributes = {}
    should_end_session = True
    reprompt_text = None

    clear()
    addrandom(getrandom())
    start()

    playing = nowplaying()
    speech_output = 'Now playing ' + playing['title'] + ' by ' + playing['artist'] + ' on ' + playing['album']
    print(speech_output)

    return build_response(session_attributes, build_speechlet_response(
        'jukebox', speech_output, reprompt_text, should_end_session))

def whatsplaying():
    session_attributes = {}
    should_end_session = True
    reprompt_text = None

    playing = nowplaying()
    speech_output = 'Now playing ' + playing['title'] + ' by ' + playing['artist'] + ' on ' + playing['album']
    print(speech_output)

    return build_response(session_attributes, build_speechlet_response(
        'jukebox', speech_output, reprompt_text, should_end_session))


# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }