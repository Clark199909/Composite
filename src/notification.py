import boto3
import json
from flask import request
from .config import get_sns_topic, get_slack_urls

# need to setup aws key and secret key before use
def notification(func):
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)

        text = f"function: {func.__name__}\n"
        text += f"args: {args}\n"
        text += f"kwargs: {kwargs}\n"
        try:
            text += f"reqeust: {request.json}\n"
        except:
            pass
        text += f"response: {repr(response)}\n"
        try:
            sns = boto3.resource('sns')
            topic = sns.Topic(get_sns_topic())
            for url in get_slack_urls():
                message = {'url': url, 'message': text}
                topic.publish(Message = json.dumps(message))
        except:
            print("error: notification not sent")
        return response
    return wrapper
