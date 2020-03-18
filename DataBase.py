import pymongo
import time

client = pymongo.MongoClient(
    'mongodb://StoreAdmin:nimdAerotS213@ds125479.mlab.com:25479/heroku_zmq98kdk?retryWrites=false')
clients_db = client.get_database()["users_db"]
users_db = client.get_database()["carma_db"]
queue_db = client.get_database()["queue_db"]


def data_base_error_decorator(func):
    def wrapper(*args):
        try:
            func(*args)
        except TimeoutError:
            with open('log.txt', 'a') as log:
                log.write(time.ctime() + ' Data base timeout error\n')
        except Exception:
            with open('log.txt', 'a') as log:
                log.write(time.ctime() + ' Other data base error\n')
    return wrapper

@data_base_error_decorator
def create_queue(id):
    if not queue_db.find_one({'queued_id': id}):
        user_queued = {'queued_id': id}
        queue_db.insert_one(user_queued)

@data_base_error_decorator
def remove_from_queue(id):
    if queue_db.find_one({'queued_id': id}):
        queue_db.find_one_and_delete({'queued_id': id})


@data_base_error_decorator
def create_user(id, first_name, last_name, request, phone_number):
    if not clients_db.find_one({'user_id': id}):
        user_request = {
            'user_id': id,
            'user_first_name': first_name,
            'user_last_name': last_name,
            'user_request': request,
            'phone_number': phone_number
        }
        clients_db.insert_one(user_request)
    else:
        print('already')


@data_base_error_decorator
def delete_user(id):
    if clients_db.find_one({'user_id': id}):
        clients_db.find_one_and_delete({'user_id': id})
        return 1
    else:
        return 0


@data_base_error_decorator
def create_user_for_carma(id, first_name, last_name):
    if not users_db.find_one({'user_id': id}):
        user_request = {
            'user_id': id,
            'user_first_name': first_name,
            'user_last_name': last_name,
            'carma_points': 0,
            'orders': [],
            'phone_number': ''
        }
        users_db.insert_one(user_request)
    else:
        print('already')


@data_base_error_decorator
def modify_carma_and_orders(id, carma_points, orders):
    users_db.find_one_and_update({'user_id': id},
                                 {'$set': {'carma_points': carma_points, 'orders': orders}})


@data_base_error_decorator
def modify_phone_number(id, phone_number):
    users_db.find_one_and_update({'user_id':id},
                                 {'$set': {'phone_number': phone_number}})