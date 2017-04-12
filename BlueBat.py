"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import urllib2
import json

categories = {
    "animals" : 27,
    "general knowledge" : 9,
    "music" : 12
}

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

#returns a dictionary. Storing attributes... maybe
def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome" #comes up on the app
    speech_output = "Welcome to the blue bat quiz game. " \
                    "Do you want to pick a topic, shuffle all questions or do you want me to list all the topics. "
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Do you want to pick a topic, shuffle all questions or do you want me to list all the topics. " #if user doesnt answer
    should_end_session = False
    speechlet_response = build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session)
    return build_response(session_attributes, speechlet_response)


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()

def setModeAndAskNumber(attributes, modeSpeech):
    playersPrompt = "How many people are playing?"
    return build_response(attributes, build_speechlet_response(playersPrompt, modeSpeech + playersPrompt, playersPrompt, False))


def list_all_topics():
    session_attributes = {}
    speech_output = "The topics are "
    category_list = categories.keys()
    for x in range(0, len(category_list) - 1):
        speech_output = speech_output + ", " + category_list[x]
    speech_output = speech_output + ", and , " + category_list[-1]

    reprompt_text = "Choose a topic by saying the topic name."  # if user doesnt answer
    should_end_session = False
    speechlet_response = build_speechlet_response("List of topics", speech_output, reprompt_text, should_end_session)
    return build_response(session_attributes, speechlet_response)

def generate_question(speech_output, attributes):
    api_question = getQuestion(categories[attributes["topic"]]) #gets all of the information about a question
    attributes["api_question"] = api_question # saving api_question with existing attributes

    # question["question"] means that it only returns the value that fits with the question key
    speechlet_response = build_speechlet_response("Question", speech_output + api_question["question"] + " true or false?" , api_question["question"] + " true or false?" , False)
    return build_response(attributes, speechlet_response)

def getQuestion(categoryNumber):
    url = 'https://opentdb.com/api.php?amount=1&category=' + str(categoryNumber) + '&type=boolean' #makes the url with the right category number
    jsonString = urllib2.urlopen(url).read() #makes it into python from json
    return json.loads(jsonString)["results"][0] #returns the entire question with all the information attatched

def start_game(numberOfPlayers, attributes):
    if(numberOfPlayers == "1"):
        speech_output = "You have chosen singleplayer mode, "
    else:
        speech_output = "You have chosen multiplayer mode with " + numberOfPlayers + " players, "
    return generate_question(speech_output, attributes)


def evaluate(answer, attributes):
    if(str(answer) == attributes["api_question"]["correct_answer"]):
        speech_output = "Your answer is correct, congratulations!"
    else:
        speech_output = "Your answer is wrong. Too bad "
    return generate_question(speech_output, attributes)

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    print(session)

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "RandomModeIntent":
        return setModeAndAskNumber({"mode": "random"}, "You have chosen random mode. ")

    if intent_name == "ChooseTopicIntent":
        topic = intent['slots']['ChosenTopic']['value']
        return setModeAndAskNumber({"mode": "chosen", "topic": topic}, "You have chosen " + topic + " mode. ")

    if intent_name == "ListModeIntent":
        return list_all_topics()

    if intent_name == "NumberOfPlayersIntent":
        numberOfPlayers = intent['slots']['NumberOfPlayers']['value']
        attributes = {"players": numberOfPlayers} #making a new attribute for number of players.
        return start_game(numberOfPlayers, session['attributes']) #lookins in attributes for the current topic value

    if intent_name == "RepeatQuestionIntent":
        question = session['attributes']['api_question']['question'] + " true or false?" #looking at the attributes for the whole question slot and finding the actual question
        speechlet_response = build_speechlet_response("Question", question, question, False)
        return build_response({}, speechlet_response)

    if intent_name == "TrueIntent":
        return evaluate(True, session['attributes'])

    if intent_name == "FalseIntent":
        return evaluate(False, session['attributes'])

    if intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()

    if intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def lambda_handler(event, context): #this is where it starts from. Our main
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

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
