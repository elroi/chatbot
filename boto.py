"""
This is the template server side for ChatBot
"""
from bottle import route, run, template, static_file, request, response
import json
import user_input_handler


#
# first_interaction = True
#

@route('/', method='GET')
def index():
    return template("chatbot.html")


@route("/chat", method='POST')
def chat():
    user_message = request.POST.get('msg')
    user_cookies = request.get_cookie('user_name')
    user_input_handler.debug_log('user_cookies: ' + str(user_cookies))

    reply = user_input_handler.analyze_input(user_message)
    user_input_handler.debug_log('in chat, reply: ' + json.dumps(reply))
    #
    if user_input_handler.user_name != None:
        response.set_cookie('user_name', user_input_handler.user_name)
    return json.dumps(reply)
    # return json.dumps({"animation": "inlove", "msg": reply})


@route("/test", method='POST')
def chat():
    user_message = request.POST.get('msg')
    return json.dumps({"animation": "inlove", "msg": user_message})


@route('/js/<filename:re:.*\.js>', method='GET')
def javascripts(filename):
    return static_file(filename, root='js')


@route('/css/<filename:re:.*\.css>', method='GET')
def stylesheets(filename):
    return static_file(filename, root='css')


@route('/images/<filename:re:.*\.(jpg|png|gif|ico)>', method='GET')
def images(filename):
    return static_file(filename, root='images')


def main():
    run(host='localhost', port=7000)

if __name__ == '__main__':
    main()
