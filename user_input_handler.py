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
# fresh_cookies = False

animation_list = ['afraid', 'bored', 'confused', 'crying', 'dancing', 'dog', 'excited', 'giggling', 'heartbroke',
                  'inlove', 'laughing', 'money', 'no', 'ok', 'takeoff', 'waiting']

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


def debug_log(inputMessage):
    if debug_mode:
        print("DEBUG message: " + str(inputMessage))


# Global setup - END

def analyze_input(user_message):
    reply_text = ""
    is_profane = check_profanity(user_message)
    debug_log('is_profane: ' + str(is_profane))
    sentiment_analyzer_scores(user_message)
    reply_animation = get_animation(user_message)
    debug_log('analyze_input, reply_animation: ' + reply_animation)
    if user_message[-1] == "!":
        reply_text = handle_statement(user_message)
    elif user_message[-1] == "?":
        reply_text = handle_question(user_message)
    elif "joke" in user_message:
        reply_text = get_chuck_norris_jokes()
        reply_animation = get_animation('funny')
    elif look_for_a_name(user_message):
        reply_text = handle_name(user_message)
        reply_animation = get_animation('excited')
        # store name cookie
    else:
        reply_text = to_upper(user_message)
    reply = {"animation": reply_animation, "msg": reply_text}
    debug_log('in analyze_input, reply: ' + json.dumps(reply))
    return reply


def sentiment_analyzer_scores(sentence):
    score = analyser.polarity_scores(sentence)
    print("{:-<40} {}".format(sentence, str(score)))


def check_profanity(user_message):
    debug_log('user_message: ' + user_message)
    user_message_words = re.compile("\W+").split(user_message)
    actual_words_in_user_message = [word for word in user_message_words if len(word) > 1]
    if len(actual_words_in_user_message) < 1:
        return False
    else:
        debug_log('user_message_words: ' + str(actual_words_in_user_message))
        overall_profanity = sum(predict(actual_words_in_user_message))
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
    name_separators = ["name is","call me"]
    for name_separator in name_separators:
        if name_separator in user_message:
            name = user_message.split(name_separator)[1]
    debug_log('name: ' + name)
    name_talkback_prefixes = ["Well hello there ","Nice to meet you ","Welcome "]
    name_talkback_postfixes = [", very nice to meet you indeed!",", welcome!",", glad you could join us!"]
    reply = random.choice(name_talkback_prefixes) + name + random.choice(name_talkback_postfixes)
    return reply

# def save_in_cookie(key, value):
    