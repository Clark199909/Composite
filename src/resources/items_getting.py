import requests
from src.config import get_courses_url
from src.config import get_students_url
from src.config import get_contacts_url


def name_getting(uni):
    url = get_students_url() + "/api/students/" + uni
    r = requests.get(url)
    content = r.json()[0]
    name = content['first_name'] + ', ' + content['last_name']
    return name

def email_getting(uni):
    url = get_contacts_url() + "/api/contacts/" + uni + "/all_emails"
    r = requests.get(url)
    if r.json():
        content = r.json()[0]
        return content['address']
    else:
        return ''