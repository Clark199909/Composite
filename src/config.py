import os

__config = {'students': 'http://127.0.0.1:5012',
            'courses': 'http://127.0.0.1:5013',
            'contacts': 'http://127.0.0.1:5014',
            }

def get_students_url():
    return __config['students']

def get_courses_url():
    return __config['courses']

def get_contacts_url():
    return __config['contacts']

def get_sns_topic():
    return os.environ.get('sns_topic')

def get_slack_urls():
    slack_urls_str = os.environ.get('slack_urls')
    return [] if slack_urls_str is None else [entry for entry in slack_urls_str.split(';') if len(entry) > 0]

def get_smarty_auth_id():
    return os.environ.get('smarty_auth_id')

def get_smarty_auth_token():
    return os.environ.get('smarty_auth_token')

