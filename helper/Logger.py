import sys, logging

class Logger:
    def __init__(self):
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    @staticmethod
    def info(msg, writeToFile = False, filepath = None):
        logging.info(f'[INFO] {msg}')
        if writeToFile:
            with open(rf'{filepath}', 'a') as reportFile:
                reportFile.write(f'{msg}\n')
    @staticmethod
    def error(msg):
        logging.error(f'[ERROR] {msg}')
    @staticmethod
    def debug(msg):
        logging.debug(f'[DEBUG] {msg}')