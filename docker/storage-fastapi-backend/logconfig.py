import os
import logging
import config

DEBUG = config.defaults['DEBUG']
VERBOSE_SUPERB = config.defaults['VERBOSE_SUPERB']
#DEBUG=False
#VERBOSE_SUPERB=False

logger = logging.getLogger('my_logger')
logger.propagate = False

# check if /storage/testApi/logs/ exists, if not create it
if not os.path.exists('/storage/testApi/logs/'):
    os.makedirs('/storage/testApi/logs/')

# Add a file handler to write logs to a file
file_handler = logging.FileHandler('/storage/testApi/logs/docker.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s [%(filename)s:%(lineno)s]', '%Y-%m-%d %H:%M:%S'))
logger.addHandler(file_handler)

# Add a stream handler to write logs to the console
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s [%(filename)s:%(lineno)s]', '%Y-%m-%d %H:%M:%S'))
if VERBOSE_SUPERB:
    console_handler.setLevel(logging.DEBUG)
elif DEBUG:
    console_handler.setLevel(logging.INFO)
else:
    console_handler.setLevel(logging.WARNING)
logger.addHandler(console_handler)

if VERBOSE_SUPERB:
    logger.setLevel(logging.DEBUG)
elif DEBUG:
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.WARNING)
