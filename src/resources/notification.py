import boto3
import json
from .config import get_sns_topic, get_slack_urls

# need to setup aws key and secret key before use
def notification(func):
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)

        text = f"function: {func.__name__}\n"
        text += f"args: {repr(args)}\n"
        text += f"kwargs: {repr(kwargs)}\n"
        text += f"response: {repr(response)}\n"
        sns = boto3.resource('sns')
        topic = sns.Topic(get_sns_topic())
        for url in get_slack_urls():
            message = {'url': url, 'message': text}
            topic.publish(Message = json.dumps(message))
        return response
    return wrapper
