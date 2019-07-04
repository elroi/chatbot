import random
import json

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


def analyze_input(user_message):
    # reply_text = ""
    reply_animation = get_animation(user_message)
    print('analyze_input, reply_animation: ' + reply_animation)
    if user_message[-1] == "!":
        reply_text = handle_statement(user_message)
    elif user_message[-1] == "?":
        reply_text = handle_question(user_message)
    else:
        reply_text = to_upper(user_message)
    reply = {"animation": reply_animation, "msg": reply_text}
    print('in analyze_input, reply: ' + json.dumps(reply))
    return reply


def handle_statement(user_message):
    # reply = {"animation": get_animation("afraid"),
    #          "msg": "That's a bold statement - '{}'".format(user_message)}
    reply_message = "That's a bold statement - '{}'".format(user_message)
    print('in handle_statement, reply_message: ' + reply_message)
    return reply_message


def handle_question(user_message):
    # reply = {"animation": get_animation("afraid"),
    #          "msg": "I'm afraid I'm not getting the question - '{}'".format(user_message)}
    reply_message = "I'm afraid I'm not getting the question - '{}'".format(user_message)
    return reply_message


def to_upper(user_message):
    reply = user_message.upper()
    return reply


# Return the first animation matching a word in the user's message
def get_animation(user_message):
    selected_animation = ""
    for word in user_message.split(' '):
        for animation, descriptors in animation_dictionary.items():
            if word in descriptors:
                selected_animation = animation
                print('in get_animation, selected_animation: ' + selected_animation)
    if selected_animation == "":
        return random.choice(animation_list)
    return selected_animation
