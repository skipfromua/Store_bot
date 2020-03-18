import time


def log_error_decorator(func):
    def wrapper(message):
        try:
            func(message)
        except AttributeError:
            with open('log.txt', 'a') as log:
                log.write(time.ctime() + ' Attribute Error\n')
        except IndexError:
            with open('log.txt', 'a') as log:
                log.write(time.ctime() + ' Index Error\n')
        except TypeError:
            with open('log.txt', 'a') as log:
                log.write(time.ctime() + ' Type Error\n')
        except ConnectionError:
            with open('log.txt', 'a') as log:
                log.write(time.ctime() + ' Connection Error\n')
        except Exception:
            with open('log.txt', 'a') as log:
                log.write(time.ctime() + ' Unknown Error\n')
    return wrapper
