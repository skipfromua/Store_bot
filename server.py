import flask
from config import TOKEN
from Bot_handlers import bot
import os
from telebot import types

server = flask.Flask(__name__)


@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    bot.process_new_updates([types.Update.de_json(flask.request.stream.read().decode('utf-8'))])
    return '!', 200

@server.route('/', methods=['GET'])
def index():
    bot.remove_webhook()
    bot.set_webhook(url='https://bot4store.herokuapp.com/{}'.format(TOKEN))
    return "Hello from heroku", 200


if __name__ == '__main__':
    server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))