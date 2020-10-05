"""
Messaging module is for sending notifications over firebase messaging service
it supports per user notification using the notification token and
per topic notification using the topic name.
requires the firebase credentials to be initialized first.
ENJOY!
"""

from django.conf import settings
from firebase_admin import messaging
import logging

logger = logging.getLogger(__name__)


def notify_user(notifications_token: str, message: dict):
    """
    Notifies a user using his notifications token (provided from the apps)
    :param notifications_token: the user's notification token
    :param message: the message should be a dict normal use case consists of two keys (title,message)
    :return: None
    """
    if notifications_token == '' or notifications_token is None:
        raise ValueError('notifications_token must not be empty, you should provide the user\'s notification token')

    if len(message.keys()) < 2:
        raise ValueError('you must provide a message in the notification')

    if type(message) is not dict:
        raise TypeError('The message must be a dictionary containing a title and message')

    if message['title'] is None:
        message['title'] = settings.APP_NAME

    msg = messaging.Message(data=message, token=notifications_token)
    response = messaging.send(msg)
    print(response)
    logger.info(response)


def notify_topic(message: dict, topic: str):
    _notify_topic(message, topic)


def _notify_topic(message: dict, topic):
    """
    sends notifications per topic
    :param message: the message should be a dict normal use case consists of two keys (title,message)
    :param topic: a topic name, topics are to be initialized from the receiving apps (users subscribe to topics)
    :return: None
    """
    msg = messaging.Message(data=message, topic=topic)
    response = messaging.send(msg)
    logger.info(response)
