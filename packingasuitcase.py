new = True 
true_list = []
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
    if (event['session']['application']['applicationId'] !=
             "amzn1.echo-sdk-ams.app.cb506107-ffc0-4908-97d2-6f219b4035c9"):
         raise ValueError("Invalid Application ID")

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
    intentName = intent_request['intent']['name']

    #dispatch custom intents to handlers here
    if "packingSuitcase" == intentName:
        return packing_suitcase(intent, session)
    elif "AMAZON.HelpIntent" == intentName or "AMAZON.StartOverIntent" == intentName:
        return get_welcome_response()
    elif "AMAZON.CancelIntent" == intentName or "AMAZON.StopIntent" == intentName:
        return handle_session_end_request()
    elif "AMAZON.NextIntent" == intentName:
        return skip_instructions()
        

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------

def skip_instructions():
    global new
    new = True
    global true_list
    true_list = []
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Skipped. " \
                    "Player One, what are you packing? "
    reprompt_text = "Player One, what are you packing? "
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
    


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    global new
    new = True
    global true_list
    true_list = []
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Packing a Suitcase. " \
                    "First, Player One will tell me an item to pack. " \
                    "Next player will say the item followed by " \
                    "a new item, continuing until one player " \
                    "is incorrect or says an item out of order. " \
                    "Player One, what are you packing? "

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Player One, what item are you packing? "
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))



def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for playing Packing a Suitcase. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))
        

        
def end_game(session_attributes):
    card_title = session_attributes
    
    speech_output = "Game over! " \
                    "Would you like to play again? Say restart if yes. " \
                    "I'll automatically end the game if no. "
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, None, should_end_session))
    
        
def packing_suitcase(intent, session):
   
    session_attributes = {}
    should_end_session = False
    # true_list is what is in the suitcase
    list_of_items = intent['slots']['Items']['value']
    # if first item packed, add to correct list of items packed
    if new:
        global true_list
        true_list.append(list_of_items)
        global new 
        new = False
        speech_output = "Next player, what would you like to pack? "
        reprompt_text = "Next player, what would you like to pack? "
    # else check if items said were correct
    # if not, game over
    # if correct, add last item to true list
    else:
        # user_items is list of items said by Player
        user_items = list_of_items.split("and")
        
        # if user tries to pack more or less than 1 additional item
        if len(user_items) > (len(true_list) + 1):
            speech_output = "Sorry, you can only pack one extra item. " \
                            "Please revise and tell me what you'd like to pack. "
            reprompt_text = "Sorry, you can only pack one extra item. " \
                            "Please revise and tell me what you'd like to pack. "
        else:
            # loop through list of items, if anything wrong, game over
            for i in range(len(true_list)):
                true_list[i] = true_list[i].strip()
                user_items[i] = user_items[i].strip()
                if true_list[i] != user_items[i]:
                    session_attributes = true_list[i] + "," + user_items[i]
                    return end_game(session_attributes)
            # if correct, add the first new item said to true list
            speech_output = "Correct! Next player, what would you like to pack? "
            reprompt_text = "Correct! Next player, what would you like to pack? "
            global true_list
            true_list.append(user_items[len(true_list)])
        
    card_title = true_list[0]
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
    

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