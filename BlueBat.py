"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6
jhh
For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import urllib2
import json

categories = {
    "animals": 27,
    "general knowledge": 9,
    "music": 12,
    "movies":  11,
    "computers": 18,
    "video games": 15,
    "gadgets": 30,
    "cartoons": 32,
    "science": 17
}

# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session, cardImage=None):

    response = {'outputSpeech': {'type': 'PlainText', 'text': output},
                'card': {'type': 'Simple', 'title': title, 'content': cardOutput},
                'reprompt': {'outputSpeech': {'type': 'PlainText', 'text': reprompt_text}},
                'shouldEndSession': should_end_session}

    if cardImage != None:
        response['card']['image'] = {
            "smallImageUrl": cardImage,
            "largeImageUrl": cardImage
        }

    return response


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
    card_title = "Welcome"  # comes up on the app
    speech_output = "Welcome to the blue bat quiz game. " \
                    "Do you want to pick a topic, shuffle all questions or do you want me to list all the topics. "
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Do you want to pick a topic, shuffle all questions or do you want me to list all the topics. "  # if user doesnt answer
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
    attributes["state"] = "waitingForNumberOfPlayers"
    playersPrompt = "How many people are playing? The game supports up to 5 players."
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
    currentPlayer = attributes['questionNumber'] % attributes['numberOfPlayers']
    if "topic" in attributes:
        url = 'https://opentdb.com/api.php?amount=1&category=' + str(categories[attributes["topic"]]) + '&type=boolean'  # makes the url with the right category number
    else:
        url = 'https://opentdb.com/api.php?amount=1&type=boolean'
    api_question = getQuestion(url)  # gets all of the information about a question
    attributes["api_question"] = api_question  # saving api_question with existing attributes
    if attributes['numberOfPlayers'] > 1:
        speech_output = speech_output + " Player " + str(currentPlayer + 1) + ": "
    speech_output = speech_output + api_question["question"] + " True or false?"

    # question["question"] means that it only returns the value that fits with the question key
    speechlet_response = build_speechlet_response("Question", speech_output, api_question["question"] + " True or false?", False)

    return build_response(attributes, speechlet_response)


def getQuestion(url):
    jsonString = urllib2.urlopen(url).read()  # makes it into python from json
    return json.loads(jsonString)["results"][0]  # returns the entire question with all the information attatched


def start_game(attributes):
    attributes["state"] = "inGame"
    numberOfPlayers = attributes['numberOfPlayers']
    attributes["score"] = {}
    for x in range(0, numberOfPlayers):
        attributes["score"][str(x)] = 0
    if numberOfPlayers == 1:
        speech_output = "You have chosen singleplayer mode, "
    else:
        speech_output = "You have chosen multiplayer mode with " + str(numberOfPlayers) + " players, "
    return generate_question(speech_output, attributes)


def evaluate(answer, attributes):
    currentPlayer = attributes['questionNumber'] % attributes['numberOfPlayers']
    if str(answer) == attributes["api_question"]["correct_answer"]:
        attributes["score"][str(currentPlayer)] = attributes["score"][str(currentPlayer)] + 1
        speech_output = "Your answer is correct, congratulations! "
    else:
        speech_output = "Your answer is wrong. Too bad.  "
    currentScore = attributes["score"][str(currentPlayer)]
    if attributes['numberOfPlayers'] == 1:
        speech_output = speech_output + " You have " + str(currentScore) + " point"
    else:
        speech_output = speech_output + " Player " + str(currentPlayer + 1) + " has " + str(currentScore) + " point"
    if currentScore == 1:
        speech_output = speech_output + ". "
    else:
        speech_output = speech_output + "s. "
    attributes['questionNumber'] = attributes['questionNumber'] + 1
    return generate_question(speech_output, attributes)


def endGame(attributes):
    speech_output = "You ended the game. "
    if(attributes['numberOfPlayers'] == 1):
        speech_output = speech_output + "Your final score is: " + str(attributes["score"]["0"]) + " point"
        if (attributes['score']["0"] != 1):
            speech_output = speech_output + "s. "
    else:
        speech_output = speech_output + "The final scores are: "
        players = attributes['score'].keys()
        players.sort(key = lambda x: attributes['score'][x], reverse = True)
        speech_output = speech_output + "Player " + str(int(players[0])+1) + " has won with a total of " + str(attributes['score'][players[0]]) + "point"
        if attributes['score'][players[0]] != 1:
            speech_output = speech_output + "s. "
        for player in players[1:]:
            score = attributes['score'][player]
            speech_output = speech_output + "Player " + str(int(player)+1) + " has " + str(score) + " point"
            if attributes['score'][player] != 1:
                speech_output = speech_output + "s, "
            else:
                speech_output = speech_output + ", "
    speechlet_response = build_speechlet_response("End Game", speech_output, "", True)
    return build_response(attributes, speechlet_response)


def invalidIntent(attributes):
    speech_output = "Wot mate?"
    speechlet_response = build_speechlet_response("WOT", speech_output, "", False)
    return build_response(attributes, speechlet_response)


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    print(session)

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "RandomModeIntent":
        if "attributes" in session and "state" in session['attributes']:
            return invalidIntent(session["attributes"])

        return setModeAndAskNumber({"mode": "random"}, "You have chosen random mode. ")

    if intent_name == "ChooseTopicIntent":
        if "attributes" in session and "state" in session['attributes']:
            return invalidIntent(session["attributes"])
        topic = intent['slots']['ChosenTopic']['value']
        return setModeAndAskNumber({"mode": "chosen", "topic": topic}, "You have chosen " + topic + ". ")

    if intent_name == "ListModeIntent":
        if "attributes" in session and "state" in session['attributes']:
            return invalidIntent(session["attributes"])
        return list_all_topics()

    if intent_name == "NumberOfPlayersIntent":
        if ("attributes" not in session or "state" not in session['attributes'] or session['attributes']['state'] != "waitingForNumberOfPlayers"):
            return invalidIntent(session.get("attributes", {}))
        numberOfPlayers = intent['slots']['NumberOfPlayers']['value']
        attributes = session['attributes']
        attributes['numberOfPlayers'] = int(numberOfPlayers)
        attributes['questionNumber'] = 0
        return start_game(attributes)  # looking in attributes for the current topic value

    if intent_name == "RepeatQuestionIntent":
        if "attributes" not in session or "state" not in session['attributes'] or session['attributes']['state'] != "inGame":
            return invalidIntent(session.get("attributes", {}))
        question = session['attributes']['api_question']['question'] + " true or false?"  # looking at the attributes for the whole question slot and finding the actual question
        speechlet_response = build_speechlet_response("Question", question, question, False)
        return build_response({}, speechlet_response)

    if intent_name == "TrueIntent":
        if "attributes" not in session or "state" not in session['attributes'] or session['attributes']['state'] != "inGame":
            return invalidIntent(session.get("attributes", {}))
        return evaluate(True, session['attributes'])

    if intent_name == "FalseIntent":
        if "attributes" not in session or "state" not in session['attributes'] or session['attributes']['state'] != "inGame":
            return invalidIntent(session.get("attributes", {}))
        return evaluate(False, session['attributes'])

    if intent_name == "EndGameIntent":  # reads score and finishes game
        if "attributes" not in session or "state" not in session['attributes'] or session['attributes']['state'] != "inGame":
            return invalidIntent(session.get("attributes", {}))
        return endGame(session['attributes'])

    if intent_name == "FatSnakeIntent":
        speechlet_response = build_speechlet_response("Easter Egg", "Too fat to snake! hissssssssssssss", "hissssssssssssss!", False)
        return build_response({}, speechlet_response)

    if intent_name == "CreditIntent":
        output = "This piece of art was brought into existence in 2017 by the following blue bats: Alistair Smith aka Flight of Stairs, Katie Worton aka Catamorpheus, Linea Katrine Wesnaes aka Lineakat, Theodora Zamfirache aka iunodora."
        cardImage = "http://www.clipartlord.com/wp-content/uploads/2016/09/bat19.png"
        speechlet_response = build_speechlet_response("Credits", output, "3 kewl 5 u", False, cardImage)
        return build_response({}, speechlet_response)

    if intent_name == "SkinnyPigeonIntent":
        speechlet_response = build_speechlet_response("Easter Egg", "I like seeds. Peep peep.", "peep peep, I'm pigeon, yay!", False)
        return build_response({}, speechlet_response)

    if intent_name == "BlueBatIntent":
        speechlet_response = build_speechlet_response("BlueBats", "You won a prize. Check your phone. ", "Seriously. Check your phone. Now. Do it. Check your phone.", False)
        return build_response({}, speechlet_response)

    if intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()

    if intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def lambda_handler(event, context):  # this is where it starts from. Our main
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
