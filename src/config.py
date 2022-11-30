# TODO consider using config or db to get these settings
__config = {'students': 'http://127.0.0.1:5012',
            'courses': 'http://127.0.0.1:5013',
            'contacts': 'http://127.0.0.1:5014',
            'sns_topic': "arn:aws:sns:us-east-1:xxx:6156_db_update",
            'slack_urls': ['https://hooks.slack.com/services/xxx/xxxxx'],
            }

def get_students_url():
    return __config['students']

def get_courses_url():
    return __config['courses']

def get_contacts_url():
    return __config['contacts']

def get_sns_topic():
    return __config['sns_topic']

def get_slack_urls():
    return __config['slack_urls']
