'''
logger_setup.py customizes the app's logging module. Each time an event is
logged the logger checks the level of the event (eg. debug, warning, info...).
If the event is above the approved threshold then it goes through. The handlers
do the same thing; they output to a file/shell if the event level is above their
threshold.
:Example:
        >>> from website import logger
        >>> logger.info('event', foo='bar')
**Levels**:
        - logger.debug('For debugging purposes')
        - logger.info('An event occured, for example a database update')
        - logger.warning('Rare situation')
        - logger.error('Something went wrong')
        - logger.critical('Very very bad')
You can build a log incrementally as so:
        >>> log = logger.new(date='now')
        >>> log = log.bind(weather='rainy')
        >>> log.info('user logged in', user='John')
'''

import datetime as dt
import logging
from logging.handlers import RotatingFileHandler
import pytz

from flask import request, session
from structlog import wrap_logger
from structlog.processors import JSONRenderer

from app import app, config

# Set the logging level
app.logger.setLevel(app.config['LOG_LEVEL'])

# Remove the stdout handler
app.logger.removeHandler(app.logger.handlers[0])

TZ = pytz.timezone(app.config['TIMEZONE'])

def add_fields(_, level, event_dict):
    ''' Add custom fields to each record. '''
    now = dt.datetime.now()
    event_dict['timestamp'] = TZ.localize(now, True).astimezone(pytz.utc).isoformat()
    event_dict['level'] = level

    if session:
        event_dict['session_id'] = session.get('session_id')

    if request:
        try:

            event_dict['ip_address'] = request.remote_addr
        except:
            event_dict['ip_address'] = 'unknown'

    return event_dict

# Add a handler to write log messages to a file
if app.config.get('LOG_FILE'):
    file_handler = RotatingFileHandler(app.config['LOG_ACTIVITY'],
                                       app.config['LOG_MAXBYTES'],
                                       app.config['LOG_BACKUPS'],
                                       'a',
                                       encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    config.activitylog.addHandler(file_handler)

    file_handler = RotatingFileHandler(app.config['LOG_ERROR'],
                                       app.config['LOG_MAXBYTES'],
                                       app.config['LOG_BACKUPS'],
                                       'a',
                                       encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    config.errorlog.addHandler(file_handler)

# Wrap the application logger with structlog to format the output
logger = wrap_logger(
    app.logger,
    processors=[
        add_fields,
        JSONRenderer(indent=None)
    ]
)
errorlog = wrap_logger(
    config.errorlog,
    processors=[
        add_fields,
        JSONRenderer(indent=None)
    ]
)
activitylog = wrap_logger(
    config.activitylog,
    processors=[
        add_fields,
        JSONRenderer(indent=None)
    ]
)
