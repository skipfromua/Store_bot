import telebot
from config import TOKEN
from telebot import types
from DataBase import *
from log import log_error_decorator
from text import *

bot = telebot.TeleBot(token=TOKEN)


@bot.message_handler(commands=['start'])
@log_error_decorator
def start(message):
    last_name = correct_last_name(message.from_user.last_name)
    create_user_for_carma(message.from_user.id, message.from_user.first_name, last_name)
    auth(message)
    if users_db.find_one({'user_id': message.chat.id})['phone_number'] \
            or message.chat.username:
        start_point(message)
    else:
        bot.send_message(message.chat.id, 'У вас отсутствует имя пользователя, добавьте его '
                                          'или поделитесь с ботом номером телефона, нажав на кнопку внизу.')
        get_phone(message)


@bot.message_handler(commands=['help'])
@log_error_decorator
def help(message):
    bot.send_message(message.chat.id, HELP_TEXT)


@bot.message_handler(content_types=['contact'])
@log_error_decorator
def test(message):
    clear_markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, 'ОК!', reply_markup=clear_markup)
    if message.chat.id == message.contact.user_id:
        modify_phone_number(message.chat.id, message.contact.phone_number)
        start_point(message)
    else:
        bot.send_message(message.chat.id, 'Это не ваш контакт. Для корректной работы - отправьте свой.')


@bot.callback_query_handler(func=lambda call: True)
@log_error_decorator
def callback_inline(call):
    last_name = correct_last_name(call.message.chat.last_name)
    if call.message:
        if call.data == 'i_need':
            if not queue_db.find_one({'queued_id': call.from_user.id}) in queue_db.find() and not clients_db.find_one(
                    {'user_id': call.from_user.id}) in clients_db.find():
                create_queue(call.from_user.id)
                bot.send_message(call.message.chat.id,
                                 text='Напишите, что вам нужно в магазине и укажите в свою комнату')
            else:
                if clients_db.find_one({'user_id': call.from_user.id}):
                    bot.send_message(call.message.chat.id,
                                     text='Вы уже сделали 1 заказ, пока это ограничение, '
                                          'если хотите что-то изменить, удалите станый заказ и '
                                          'сделайте новый')
                else:
                    bot.send_message(call.message.chat.id,
                                     text='Вы всё ещё не написали что вам нужно в магазине.')
        elif call.data == 'i_am_there':
            bot.send_message(call.message.chat.id,
                             text="Список нуждающихся:", reply_markup=keyboard())
        elif call.data == 'cancel':  # Если сообщение из чата с ботом
            if not delete_user(call.message.chat.id):
                bot.send_message(call.message.chat.id,
                                 text='У вас нет активных заказов.')
            else:
                bot.send_message(call.from_user.id,
                                 text='Заказ успешно удален.')
        elif call.data == 'accept':
            try:
                new_list_of_orders = users_db.find_one({'user_id': call.message.chat.id})['orders']
                new_list_of_orders.pop(-1)
                order_id = users_db.find_one({'user_id': call.message.chat.id})['orders'].pop(-1)

                if call.from_user.username:  # this func to rewrite
                    bot.send_message(order_id,
                                     text='Ваш заказ принял ' + call.from_user.first_name + ' ' +
                                          last_name + ' (@' + call.from_user.username + ')')
                else:
                    bot.send_message(order_id,
                                     text='Ваш заказ принял ' + call.from_user.first_name + ' ' +
                                          last_name)
                    bot.send_contact(order_id, users_db.find_one({'user_id': call.message.chat.id})['phone_number'],
                                     call.message.chat.first_name, last_name)

                if bot.get_chat_member(order_id, order_id).user.username:
                    bot.send_message(order_id, 'Вы приняли заказ @' +
                                     bot.get_chat_member(order_id, order_id).user.username)
                else:
                    bot.send_contact(call.message.chat.id, clients_db.find_one({'user_id': order_id})['phone_number'],
                                     bot.get_chat_member(order_id, order_id).user.first_name,
                                     bot.get_chat_member(order_id, order_id).user.last_name)
                delete_user(order_id)
                modify_carma_and_orders(call.from_user.id,
                                        users_db.find_one({'user_id': call.message.chat.id})['carma_points'],
                                        new_list_of_orders)

            except IndexError:
                bot.send_message(call.from_user.id,
                                 text='Вы не можете принять, раннее принятый заказ'
                                      '(возможно принятый не вами).'
                                      'Обновте список тех, кому что-то нужно в магазине.')
        elif call.data == 'denied':
            try:
                new_list_of_orders = users_db.find_one({'user_id': call.message.chat.id})['orders']
                new_list_of_orders.pop(-1)
                modify_carma_and_orders(call.message.chat.id,
                                        users_db.find_one({'user_id': call.message.chat.id})['carma_points'] - 1,
                                        new_list_of_orders)
                bot.send_message(call.message.chat.id,
                                 text='Список нуждающихся:',
                                 reply_markup=keyboard())
            except IndexError:
                bot.send_message(call.from_user.id,
                                 text='Вы не можете отменить, раннее принятый заказ '
                                      '(возможно принятый не вами).'
                                      'Обновте список тех, кому что-то нужно в магазине.')
        else:
            try:
                bot.send_message(call.message.chat.id,
                                 text=clients_db.find_one({'user_id': int(call.data)})['user_request'],
                                 reply_markup=confirm(call.data, call.message.chat.id))
            except TypeError:
                bot.send_message(call.from_user.id,
                                 text='К сожалению этот заказ больше не актуален, '
                                      'обновите список заказов, нажав кнопку "Я в магазине..."')


@bot.message_handler(content_types=['text'])
@log_error_decorator
def request(message):
    last_name = correct_last_name(message.from_user.last_name)
    if users_db.find_one({'user_id': message.from_user.id})['phone_number'] or message.from_user.username:
        if queue_db.find_one({'queued_id': message.from_user.id}) in queue_db.find():
            create_user(message.from_user.id, message.from_user.first_name,
                        last_name, message.text,
                        users_db.find_one({'user_id': message.from_user.id})['phone_number'])
            remove_from_queue(message.from_user.id)
            bot.send_message(message.from_user.id, text='Вы сдедали заказ, ожидайте.')
        else:
            print('not found')
    else:
        bot.send_message(message.from_user.id, 'У вас отстутствует имя пользователя и нет вашего номера телефона в базе'
                                               ' данных, это значит что пользователь, который принял ваш заказ не '
                                               'сможет вам написать. Пожалуйста начните заново, введите команду /start')


def auth(message):
    clear_markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, 'Привет!!! Если нужна инструкция, нажми сюда /help', reply_markup=clear_markup)


def start_point(message):
    keyboard = types.InlineKeyboardMarkup()
    callback_need = types.InlineKeyboardButton(text='Мне нужно в магазине...', callback_data='i_need')
    callback_there = types.InlineKeyboardButton(text='Я в магазине...', callback_data='i_am_there')
    callback_cancel = types.InlineKeyboardButton(text='Отменить заказ', callback_data='cancel')
    keyboard.add(callback_need)
    keyboard.add(callback_there)
    keyboard.add(callback_cancel)
    bot.send_message(message.chat.id, 'Выбери нужное из списка:', reply_markup=keyboard)


def confirm(client_id, helper_id):
    keyboard = types.InlineKeyboardMarkup()
    callback_accept = types.InlineKeyboardButton(text="Принять", callback_data='accept')
    callback_denied = types.InlineKeyboardButton(text='Отклонить', callback_data='denied')
    keyboard.add(callback_accept)
    keyboard.add(callback_denied)
    carma = users_db.find_one({'user_id': int(helper_id)})['carma_points'] + 1
    orders = users_db.find_one({'user_id': int(helper_id)})['orders']
    orders.append(int(client_id))
    modify_carma_and_orders(int(helper_id), carma, orders)
    return keyboard


def keyboard():
    keyboard = types.InlineKeyboardMarkup()
    for user in clients_db.find():
        keyboard.add(types.InlineKeyboardButton(text=user['user_first_name'] + " " + user['user_last_name'],
                                                callback_data=user['user_id']))
    return keyboard


def get_phone(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = types.KeyboardButton(text="Использовать номер телефона", request_contact=True)
    keyboard.add(button_phone)
    bot.send_message(message.chat.id, "Мой контакт:", reply_markup=keyboard)


def correct_last_name(last_name):
    if not last_name:
        l_name = ''
    else:
        l_name = last_name
    return l_name

