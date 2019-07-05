import random
import json
import re
import requests
from requests.exceptions import HTTPError
from http import cookies

from profanity_check import predict, predict_prob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyser = SentimentIntensityAnalyzer()

# Global setup - START

debug_mode = True

first_interaction = True
user_name = None
# profanity_flag = False
# fresh_cookies = False

# Animations
animation_list = ['afraid', 'bored', 'confused', 'crying', 'dancing', 'dog', 'excited', 'giggling', 'heartbroke',
                  'inlove', 'laughing', 'money', 'no', 'ok', 'takeoff', 'waiting']

positive_animations = ['dancing','excited','giggling','inlove','laughing','ok']
negative_animations = ['afraid','bored','confused','crying','heartbroke','no']
neutral_animations = ['bored','waiting']
funny_animations = ['dog','money','takeoff']


animation_dictionary = {
    'afraid': ['fear', 'afraid', 'frighten'],
    'bored': ['bored', 'boring'],
    'confused': ['confused', 'confusing'],
    'crying': ['sad', 'emotional', 'crying'],
    'dancing': ['dance', 'dancing'],
    'dog': ['dog', 'puppy'],
    'excited': ['excited'],
    'giggling': ['funny'],
    'heartbroke': ['heartbroke'],
    'inlove': ['love', 'loving'],
    'laughing': ['funny'],
    'money': ['price', 'expensive'],
    'no': ['no'],
    'ok': ['ok', 'well'],
    'takeoff': ['takeoff'],
    'waiting': ['waiting']
}

# Random replies
random_replies = ["That's interesting, tell me more...","Sound's interesting.","BRB","Going to the little bot's room, coming back soon","Oh my maker!"]

# Me you dictionaries
me_words = ["I","Me","My","Mine"]
you_words = ["You","Your","Yours"]
pronoun_dictionary = {'I':'you','you':'I',
                      'my':'your', 'me':'you','your':'my'}

def debug_log(inputMessage):
    if debug_mode:
        print("DEBUG message: " + str(inputMessage))


# Global setup - END

def analyze_input(user_message):
    global first_interaction
    pronoun_swapper(user_message)
    reply_text = ""
    reply_animation = ""
    # Profanity checking - Zero tolerance for profanity
    is_profane = check_profanity(user_message)
    debug_log('is_profane: ' + str(is_profane))
    if is_profane:
        reply_text = "Why use this kind of language?"
        reply_animation = get_animation('confused')
        first_interaction = False
        return {"animation": reply_animation, "msg": reply_text}
    #
    # Get sentiment based animation
    reply_animation = sentiment_based_animation(sentiment_analyzer_scores(user_message),user_message)

    # reply_animation = get_animation(user_message) if len(reply_animation) == 0 else reply_animation
    debug_log('analyze_input, reply_animation: ' + reply_animation)
    #
    # First built-in interaction asks for a name.
    # If it is not a profanity, it will be handled as a name.
    if check_if_first_interaction(first_interaction):
        reply_text = handle_name(user_message)
        reply_animation = get_animation('excited')
        first_interaction = False
    # Handle statement
    elif user_message[-1] == "!":
        handle_statement_result = handle_statement(user_message)
        reply_text = handle_statement_result if len(
            reply_text) == 0 else reply_text + ". Also, " + handle_statement_result
    # Handle question
    elif user_message[-1] == "?":
        handle_question_result = handle_question(user_message)
        reply_text = handle_question_result if len(
            reply_text) == 0 else reply_text + ". Also, " + handle_question_result
    # Handle joke - move to question
    elif "joke" in user_message:
        reply_text = get_chuck_norris_jokes()
        reply_animation = get_animation('funny')
    # Handle name statement
    elif look_for_a_name(user_message):
        reply_text = handle_name(user_message)
        reply_animation = get_animation('excited')
    # Default handler
    else:
        # default_handler_result = to_upper(user_message)
        default_handler_result = random.choice(random_replies)
        reply_text = default_handler_result if len(reply_text) == 0 else reply_text + " " + default_handler_result
    reply = {"animation": reply_animation, "msg": reply_text}
    debug_log('in analyze_input, reply: ' + json.dumps(reply))
    return reply


def check_if_first_interaction(first_interaction):
    if first_interaction:
        first_interaction = False
        return True
    return False


def sentiment_analyzer_scores(sentence):
    score = analyser.polarity_scores(sentence)
    compound = score["compound"]
    negative = score["neg"]
    positive = score["pos"]
    neutral = score["neu"]
    debug_log("{:-<40} {}".format(sentence, str(score)))
    debug_log("compound: " + str(compound))
    return compound

def sentiment_based_animation(compound,user_message):
    word_based_animation = get_word_based_animation(user_message)
    if 0.1 > compound > -0.1:
        animation = random.choice(neutral_animations)
    elif compound > 0.1:
        animation = word_based_animation or random.choice(positive_animations)
    elif compound < -0.1:
        animation = word_based_animation or random.choice(negative_animations)
    return animation

def check_profanity(user_message):
    debug_log('user_message: ' + user_message)
    user_message_words = re.compile("\W+").split(user_message)
    actual_words_in_user_message = [word for word in user_message_words if len(word) > 1]
    if len(actual_words_in_user_message) < 1:
        return False
    else:
        debug_log('user_message_words: ' + str(actual_words_in_user_message))
        overall_profanity = sum(predict(actual_words_in_user_message))
        if overall_profanity > 0:
            return True
        debug_log('overall_profanity: ' + str(overall_profanity))
        overall_profanity_average = overall_profanity / len(actual_words_in_user_message)
        debug_log('overall_profanity_average: ' + str(overall_profanity_average))
        debug_log('profanity probability: ' + str(predict_prob(actual_words_in_user_message)))
        debug_log('profanity probability: ' + str(
            sum(predict_prob(actual_words_in_user_message)) / len(actual_words_in_user_message)))
        if overall_profanity_average > 0.5:
            return True
    return False


def handle_statement(user_message):
    reply_message = "That's a bold statement - '{}'".format(user_message)
    debug_log('in handle_statement, reply_message: ' + reply_message)
    return reply_message


def handle_question(user_message):
    reply_message = "I'm afraid I'm not getting the question - '{}'".format(user_message)
    return reply_message


def to_upper(user_message):
    reply = user_message.upper()
    return reply


# Return the first animation matching a word in the user's message
def get_animation(user_message):
    selected_animation = ""
    for word in re.compile("\W+").split(user_message):
        for animation, descriptors in animation_dictionary.items():
            if word in descriptors:
                selected_animation = animation
                debug_log('in get_animation, selected_animation: ' + selected_animation)
    if selected_animation == "":
        debug_log("random animation")
        return random.choice(animation_list)
    return selected_animation

def get_word_based_animation(user_message):
    selected_animation = ""
    for word in re.compile("\W+").split(user_message):
        for animation, descriptors in animation_dictionary.items():
            if word in descriptors:
                selected_animation = animation
                debug_log('in get_animation, selected_animation: ' + selected_animation)
    return selected_animation

def get_chuck_norris_jokes():
    api_url = "http://api.icndb.com/jokes/random"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
    except HTTPError as http_error:
        debug_log((f'Some crooked HTTPError happened: {http_error}'))
    except Exception as e:
        debug_log(f'Some darn error happened: {e}')
    else:
        debug_log('Successfull requested the joke from it\'s api!')
        if response and response.status_code == 200:
            joke_id = response.json()["value"]["id"]
            joke_text = response.json()["value"]["joke"]
            joke = 'Chuck Norris joke {}: {}'.format(joke_id, joke_text)
            debug_log(joke)
        else:
            joke = 'Chuck Norris ain\'t joking with you!'
        return joke


def look_for_a_name(user_message):
    if ("name is" or "call me") in user_message:
        return True


def handle_name(user_message):
    name_separators = ["name is", "call me"]
    name_talkback_prefixes = ["Well hello there ", "Nice to meet you ", "Welcome "]
    name_talkback_postfixes = [", very nice to meet you indeed!", ", welcome!", ", glad you could join us!"]
    name = None
    for name_separator in name_separators:
        if name_separator in user_message:
            name = user_message.split(name_separator)[1]
            # save_in_cookie("name", name)
    if name == None and check_if_first_interaction(first_interaction):
        name = user_message.capitalize()
    if name != None:
        save_name_global_variable(name.capitalize())
    debug_log('name: ' + name)
    # save_in_cookie('name',name)
    reply = random.choice(name_talkback_prefixes) + name + random.choice(name_talkback_postfixes)
    return reply

#                       'my': 'your', 'me': 'you', 'your': 'my'
# pronoun_dictionary = {'I': 'you', 'you': 'I',
def pronoun_swapper(user_message):
    # splitter = re.compile("\W+")
    split_user_message = re.compile("\W+").split(user_message)
    
    debug_log(split_user_message)


# Auxiliary functions

def save_name_global_variable(name):
    global user_name
    user_name = "" + name.strip()


def save_in_cookie(key, value):
    boto_cookie = cookies.SimpleCookie()
    boto_cookie[key] = value
    # response.set_cookie
    debug_log('boto_cookie: ' + str(boto_cookie))
    debug_log('boto_cookie.output(): ' + boto_cookie.output())
    debug_log('boto_cookie.js_output(): ' + boto_cookie.js_output())


def load_from_cookie(key):
    boto_cookie = cookies.SimpleCookie()
    return boto_cookie.load('name')
