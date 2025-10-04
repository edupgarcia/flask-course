import os


class Config(object):
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or b'J?6W1\xf4\xdd\xfc\x88d\xbdX\x10s1\xad'

    MONGODB_SETTINGS = {'db': 'UTA_Enrollment'}

    # MONGO_URI = 'mongodb://localhost:27017/UTA_Enrollment'
