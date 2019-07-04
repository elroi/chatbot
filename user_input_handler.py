import random
import json
import re

from profanity_check import predict, predict_prob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyser = SentimentIntensityAnalyzer()


# Global setup - START

debug_mode = True

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
    # reply_text = ""
    is_profane = check_profanity(user_message)
    debug_log('is_profane: ' + str(is_profane))
    sentiment_analyzer_scores(user_message)
    reply_animation = get_animation(user_message)
    debug_log('analyze_input, reply_animation: ' + reply_animation)
    if user_message[-1] == "!":
        reply_text = handle_statement(user_message)
    elif user_message[-1] == "?":
        reply_text = handle_question(user_message)
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
        debug_log('profanity probability: ' + str(sum(predict_prob(actual_words_in_user_message)) / len(actual_words_in_user_message)))
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
