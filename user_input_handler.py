import random
import json
import re
import requests
from requests.exceptions import HTTPError
from http import cookies
import time
from fuzzywuzzy import process

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

positive_animations = ['dancing', 'excited', 'giggling', 'inlove', 'laughing', 'ok']
negative_animations = ['afraid', 'bored', 'confused', 'crying', 'heartbroke', 'no']
neutral_animations = ['bored', 'waiting']
funny_animations = ['dog', 'money', 'takeoff']

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
random_replies = ["That's interesting, tell me more...", "Sound's interesting.", "BRB",
                  "Going to the little bot's room, coming back soon", "Oh my maker!"]

# Me you dictionaries
me_words = ["I", "Me", "My", "Mine"]
you_words = ["You", "Your", "Yours"]
pronoun_dictionary = {'me': 'you', 'you': 'me',
                      'my': 'your', 'your': 'my'}
gender_list = ['Male', 'Female', 'Other', 'complicated', 'none of your business']
# Default values
name = "Boto"
weather = "Cloudy"
age = time.time()
gender = ""
# Basic Q&A
basic_q_and_a = {
    "what's your name?": [
        "my name is {}".format(name),
        "you can call me {}".format(name),
        "my friends call me {}".format(name),
        "{0}, {0} the amazing bot".format(name),
        ],
    "what's today's weather?": [
        "the weather is {}".format(weather),
        "it is {} today".format(weather),
        ],
    "what's your age?": [
        "my age is {}".format(age),
        "{}, if you must know".format(age),
        "That's a rude question young human! ({})".format(age),
        ],
    "what's your gender?": [
        "my gender is {}".format(random.choice(gender_list)),
        "I was made a {}".format(random.choice(gender_list)),
        "I am {}".format(random.choice(gender_list)),
        "{}, if you're into me take a number (*in hex)".format(random.choice(gender_list)),
    ]
}
basic_statements_replies = [
    'sounds interesting!',
    'tell me more!',
    'wa wa wi wa!',
    'in your maker!',
    'why do you say that?',
    'are you certain?',
    'what makes you feel this way?',
    'how long will you keep this thought?',
    'come again?',
    ':)',
    'take that back!',
    "That's a bold statement!"
]


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
    debug_log('in analyze_input, is_profane: ' + str(is_profane))
    if is_profane:
        reply_text = "Why use this kind of language?"
        reply_animation = get_animation(random.choice(negative_animations))
        first_interaction = False
        return {"animation": reply_animation, "msg": reply_text}
    #
    # Get sentiment based animation
    reply_animation = sentiment_based_animation(sentiment_analyzer_scores(user_message), user_message)

    # reply_animation = get_animation(user_message) if len(reply_animation) == 0 else reply_animation
    debug_log('in analyze_input, reply_animation: ' + reply_animation)
    #
    # First built-in interaction asks for a name.
    # If it is not a profanity, it will be handled as a name.
    if check_if_first_interaction(first_interaction):
        reply_text = handle_name(user_message)
        reply_animation = get_animation('excited')
        first_interaction = False
    # Handle question
    elif user_message[-1] == "?":
        handle_question_result = handle_question(user_message)
        reply_text = handle_question_result if len(
            reply_text) == 0 else reply_text + ". Also, " + handle_question_result
    # Handle statement
    elif user_message[-1] == "!":
        handle_statement_result = handle_statement(user_message)
        reply_text = handle_statement_result if len(
            reply_text) == 0 else reply_text + ". Also, " + handle_statement_result
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
    debug_log('====================================')
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
    debug_log("in sentiment_analyzer_scores, {:-<40} {}".format(sentence, str(score)))
    debug_log("in sentiment_analyzer_scores, compound: " + str(compound))
    return compound


def sentiment_based_animation(compound, user_message):
    word_based_animation = get_word_based_animation(user_message)
    if 0.1 > compound > -0.1:
        animation = random.choice(neutral_animations + funny_animations)
    elif compound > 0.1:
        animation = word_based_animation or random.choice(positive_animations)
    elif compound < -0.1:
        animation = word_based_animation or random.choice(negative_animations)
    return animation


def check_profanity(user_message):
    debug_log('in check_profanity, user_message: ' + user_message)
    user_message_words = re.compile("\W+").split(user_message)
    actual_words_in_user_message = [word for word in user_message_words if len(word) > 0]
    if len(actual_words_in_user_message) < 1:
        return False
    else:
        debug_log('in check_profanity, user_message_words: ' + str(actual_words_in_user_message))
        overall_profanity = sum(predict(actual_words_in_user_message))
        if overall_profanity > 0:
            return True
        debug_log('in check_profanity, overall_profanity: ' + str(overall_profanity))
        overall_profanity_average = overall_profanity / len(actual_words_in_user_message)
        debug_log('in check_profanity, overall_profanity_average: ' + str(overall_profanity_average))
        debug_log('in check_profanity, profanity probability: ' + str(predict_prob(actual_words_in_user_message)))
        debug_log('in check_profanity, profanity probability: ' + str(
            sum(predict_prob(actual_words_in_user_message)) / len(actual_words_in_user_message)))
        if overall_profanity_average > 0.5:
            return True
    return False


def handle_statement(user_message):
    reply_message = random.choice(basic_statements_replies)
    debug_log('in handle_statement, reply_message: ' + reply_message)
    return reply_message


def handle_question(user_message):
    user_message = user_message.lower()
    if user_message in basic_q_and_a.keys():
        reply_message = random.choice(basic_q_and_a[user_message])
    else:
        highest_match = process.extractOne(user_message,basic_q_and_a.keys())
        debug_log("in handle_question, highest: " + str(highest_match))
        reply_message = "I'm afraid I'm not getting the question - '{}'".format(user_message)
    #
    # else:
    debug_log('in handle_question, reply_message: ' + reply_message)
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
        debug_log("'in get_animation, random animation")
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
        debug_log((f'in get_chuck_norris_jokes, Some crooked HTTPError happened: {http_error}'))
    except Exception as e:
        debug_log(f'in get_chuck_norris_jokes, Some darn error happened: {e}')
    else:
        debug_log('in get_chuck_norris_jokes, Successfull requested the joke from it\'s api!')
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
    debug_log('in handle_name, name: ' + name)
    # save_in_cookie('name',name)
    reply = random.choice(name_talkback_prefixes) + name + random.choice(name_talkback_postfixes)
    return reply


#                       'my': 'your', 'me': 'you', 'your': 'my'
# pronoun_dictionary = {'I': 'you', 'you': 'I',
def pronoun_swapper(user_message):
    user_message = user_message.lower()
    # splitter = re.compile("\W+")
    split_user_message = re.compile("\W+").split(user_message)
    # for word in split_user_message:
    #     if word in pronoun_dictionary.keys():
    #         return pronoun_dictionary[word]
    #     else:
    #         return word
    #
    pronoun_switched_sentence = " ".join(
        [pronoun_dictionary[word] if word in pronoun_dictionary.keys() else word for word in split_user_message])

    debug_log("in pronoun_swapper: " + pronoun_switched_sentence)
    return pronoun_switched_sentence


# Auxiliary functions

def save_name_global_variable(name):
    global user_name
    user_name = "" + name.strip()


def save_in_cookie(key, value):
    boto_cookie = cookies.SimpleCookie()
    boto_cookie[key] = value
    # response.set_cookie
    debug_log('in save_in_cookie, boto_cookie: ' + str(boto_cookie))
    debug_log('in save_in_cookie, boto_cookie.output(): ' + boto_cookie.output())
    debug_log('in save_in_cookie, boto_cookie.js_output(): ' + boto_cookie.js_output())


def load_from_cookie(key):
    boto_cookie = cookies.SimpleCookie()
    return boto_cookie.load('name')
