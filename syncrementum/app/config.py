import logging

from sqlalchemy import create_engine

TIMEZONE = 'America/Los_Angeles'


# Secret key for generating tokens
SECRET_KEY = '12345'

# API url
# API_URL='http://localhost:5001/customer_api'
AUTHORIZE_URL='https://api.instagram.com/oauth/authorize/'
# API_BASE_URL='http://localhost:5001'

LOG_FILE = True
LOG_MAXBYTES = 100000
LOG_BACKUPS = '1'

# Number of times a password is hashed
BCRYPT_LOG_ROUNDS = 12

DEBUG_TB_INTERCEPT_REDIRECTS = False

# DEBUG can only be set to True in a development environment for security reasons
DEBUG = True

#SQL Alchemy tracking of modifications
SQLALCHEMY_TRACK_MODIFICATIONS = True

LOG_LEVEL = logging.DEBUG

#set the full path of the application for the logs
LOG_ERROR = 'error.log'
LOG_ACTIVITY = 'activity.log'

errorlog = logging.getLogger("error")
activitylog = logging.getLogger("activity")
activitylog.setLevel('INFO')


#if session['error'] == True:
#    LOG_FILENAME = 'error.log'
#else:
#    LOG_FILENAME = 'activity.log'

# Configuration of a Gmail account for sending mails
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'sync4life.info@gmail.com'
MAIL_DEFAULT_SENDER = 'sync4life.info@gmail.com'
MAIL_PASSWORD = 'Bittexbuys1!'
ADMINS = ['suresha.chetu@gmail.com']

DEV_EMAIL='suresha@chetu.com'


SQLALCHEMY_DATABASE_URI = 'mysql://aksheerm:@localhost/syncrementum'
SQLALCHEMY_BINDS = {
    'syncrementum':        'mysql://aksheerm:@localhost/syncrementum',
}
engine = create_engine("mysql://aksheerm:@localhost/syncrementum",
                        pool_size=100000, max_overflow=0)

# Constants for Create Hash
PBKDF2_SALT_BYTES = 24
PBKDF2_HASH_BYTES = 24
PBKDF2_HASH_ALGORITHM = 'sha512'
PBKDF2_ITERATIONS = 1000
HASH_SECTIONS = 4
HASH_PBKDF2_INDEX = 3
HASH_SALT_INDEX = 2

instagram_username = 'aksheerchetu'
instagram_password = 'Chetu@123'

PAYPAL_MODE = "sandbox"
PAYPAL_CLIENT_ID = "AQT9_2z6t6YBCcEOYawYlRD1kqLTAuZ3QLY95x30ZM3w4aqh3CZAKM8hDK-oo3kxCHlOUFm2AnbbFnUK"
PAYPAL_CLIENT_SECRET = "ENYYwV8s9ZRXbEXCJEAOcxIYh-m1YSFKlkaqWMuApxblDA-Of9BNxF_QDxdzMsAJXHwlSRSqQAXO8JW9"
