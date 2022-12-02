import requests

COURSE_URL = "http://0.0.0.0:5011"
CONTACT_URL = "http://0.0.0.0:5012"
STUDENT_URL = "http://0.0.0.0:5013"

def name_getting(uni):
    url = STUDENT_URL + "/api/students/" + uni
    r = requests.get(url)
    content = r.json()[0]
    name = content['first_name'] + ', ' + content['last_name']
    return name

def email_getting(uni):
    url = CONTACT_URL + "/api/contacts/" + uni + "/all_emails"
    r = requests.get(url)
    if r.json():
        content = r.json()[0]
        return content['address']
    else:
        return ''