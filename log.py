import time


def log_error_decorator(func):
    def wrapper():
        try:
            func()
        except AttributeError:
            with open('log.txt', 'a') as log:
                log.write(time.ctime() + 'Attribute Error')
        except IndexError:
            with open('log.txt', 'a') as log:
                log.write(time.ctime() + 'Index Error')
        except TypeError:
            with open('log.txt', 'a') as log:
                log.write(time.ctime() + 'Type Error')
        except ConnectionError:
            with open('log.txt', 'a') as log:
                log.write(time.ctime() + 'Connection Error')
        except Exception:
            with open('log.txt', 'a') as log:
                log.write(time.ctime() + 'Unknown Error')