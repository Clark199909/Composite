from flask import request, jsonify, redirect, url_for
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)
import requests
import json

from src import app
from src.resources.contacts import ContactResource
from src.notification import notification
from src.resources.user_resource import UserResource
from src.models.user import User
from src import login_manager
from src import GOOGLE_DISCOVERY_URL
from src import GOOGLE_CLIENT_ID
from src import GOOGLE_CLIENT_SECRET
from src import client

from src.resources.students import StudentProcessing
from src.resources.contacts import ContactProcessing

from src.config import get_courses_url
from src.config import get_students_url
from src.config import get_contacts_url


white_list = {"/", "/login", "login/callback"}


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.before_request
def before_decorator():
    if request.path not in white_list and not current_user.is_authenticated:
        response = jsonify("User is not authenticated!")
        response.status_code = 400
        return response


@app.route("/")
def index():
    if current_user.is_authenticated:
        response = jsonify("User is logged in.")
        response.status_code = 200
        return response
    else:
        response = jsonify("User needs to log in.")
        response.status_code = 300
        return response


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/login")
def login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )

    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    code = request.args.get("code")

    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    user = User(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture
    )

    if not User.get(unique_id):
        UserResource.save_user(unique_id, users_name, users_email, picture)

    login_user(user)

    return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/api/students/add", methods=['POST'])
def add_new_student():
    """JSON copy to test
    {
        "uni": "ab1234",
        "first_name": "David",
        "last_name": "Martin",
        "nationality": "United States",
        "ethnicity": "White",
        "gender": "Male",
        "admission_date": "12/14/2022"
    }
    """
    data = request.json

    url_0 = get_students_url() + "/api/students/new_student"
    url_1 = get_contacts_url() + "/api/contacts/new_student"

    r_list = []
    r_list.append(requests.post(url_0, json=data).text[1:-2])
    r_list.append(requests.post(url_1, json=data).text[1:-2])
    response = jsonify(r_list)
    response.status_code = 302
    return response


@app.route("/api/students/delete", methods=['DELETE'])
def delete_a_student():
    """JSON copy to test on Postman
    {
        "uni": "ab1234"
    }
    Note: all related contacts will be also deleted
    """
    data = request.json

    url_0 = get_students_url() + "/api/students/del_student"
    url_1 = get_contacts_url() + "/api/contacts/del_student"

    r_list = []
    r_list.append(requests.delete(url_0, json=data).text[1:-2])
    r_list.append(requests.delete(url_1, json=data).text[1:-2])

    response = jsonify(r_list)
    response.status_code = 302
    return response


@app.route("/api/students/update", methods=['PUT'])
def update_a_student():
    """JSON copy to test
    {
        "uni": "ab1234",
        "first_name": "Daviiiid",
        "last_name": "Martin",
        "nationality": "United States",
        "ethnicity": "White",
        "gender": "Male",
        "admission_date": "12/14/2022"
    }
    """
    url = get_students_url() + "/api/students/update_student"
    data = request.json
    r = requests.put(url, json=data)
    body = r.text[1:-2]
    response = jsonify(body)
    response.status_code = 302
    return response


@app.route("/api/students/get/<uni>", methods=['GET'])
def get_student_by_uni(uni):
    """JSON response body be like
    [
        {
            "admission_date": "12/08/2022",
            "email": "dw3013@columbia.edu",
            "ethnicity": "Asian",
            "gender": "Female",
            "name": "Di, Wu",
            "nationality": "China",
            "uni": "dw3013"
        }
    ]
    """
    url = get_students_url() + "/api/students/" + uni
    content = requests.get(url).json()
    info = StudentProcessing.processing(content)
    response = jsonify(info)
    response.status_code = 302
    return response
    
    
# Get student (general info/contact) by name/session call_no/project name/nationality/gender
# if info_type = "info", get students' fields (like above apis) according to the attribute
# if info_type = "contacts", get students' contacts fields (like below apis) according to the attribute
# attribute is name/session call_no/project name/nationality/gender
@app.route("/api/students/<info_type>/<attribute>")
def get_students_info_or_contact_by_attribute(info_type, attribute):
    pass


@app.route("/api/students/all", methods=['GET'])
def all_student():
    """JSON respone be like
    [
        {(student info 1)},
        {(student info 2)}
    ]
    Note: if a student do not have email, his/her email will be like { email: '' }
    """
    url = get_students_url() + "/api/students"
    content = requests.get(url).json()
    info = StudentProcessing.processing(content)
    response = jsonify(info)
    response.status_code = 302
    return response


@app.route("/api/contacts/<uni>/add/<type>", methods=['POST'])
def add_new_contact(uni, type):
    """ Note: here type can be phone, email or address
    JSON copy to test on Postman (phone)
    {
        "description": "mobile",
        "country_code": "1",
        "phone_no": "3476290991"
    }
    JSON copy to test on Postman (email)
    {
        "description": "personal",
        "address": "dw3013@columbia.edu"
    }
    JSON copy to test on Postman (address)
    {
        "description": "home",
        "country": "USA",
        "state": "NY",
        "city": "NY",
        "zip_code": "10025",
        "street": "125W 109th St"
    }
    """
    if type == 'address' or type == 'email' or type == 'phone':
        url = get_contacts_url() + "/api/contacts/" + uni + "/new_"+type
        data = request.json
        r = requests.post(url, json=data)
    else:
        response = jsonify('Not existing type')
        response.status_code = 400
        return response
    body = r.text[1:-2]
    response = jsonify(body)
    response.status_code = 302
    return response


@app.route("/api/contacts/<uni>/update/<type>", methods=['PUT'])
def update_a_contact(uni, type):
    """ Note: here type can be phone, email or address
    JSON copy to test on Postman (phone)
    {
        "description": "mobile",
        "country_code": "1",
        "phone_no": "3476290992"
    }
    JSON copy to test on Postman (email)
    {
        "description": "personal",
        "address": "dw3014@columbia.edu"
    }
    JSON copy to test on Postman (address)
    {
        "description": "home",
        "country": "USA",
        "state": "NY",
        "city": "NY",
        "zip_code": "10027",
        "street": "125W 109th St"
    }
    """
    if type == 'address' or type == 'email' or type == 'phone':
        url = get_contacts_url() + "/api/contacts/" + uni + "/update_"+type
        data = request.json
        r = requests.put(url, json=data)
    else:
        response = jsonify('Not existing type')
        response.status_code = 400
        return response
    body = r.text[1:-2]
    response = jsonify(body)
    response.status_code = 302
    return response


@app.route("/api/contacts/<uni>/del/<type>", methods=['DELETE'])
def delete_a_contact(uni, type):
    """ Note: here type can be phone, email or address
    JSON copy to test on Postman (phone)
    {
        "description": "mobile"
    }
    JSON copy to test on Postman (email)
    {
        "description": "personal"
    }
    JSON copy to test on Postman (address)
    {
        "description": "home"
    }
    """
    if type == 'address' or type == 'email' or type == 'phone':
        url = get_contacts_url() + "/api/contacts/" + uni + "/del_"+type
        data = request.json
        r = requests.delete(url, json=data)
    else:
        response = jsonify('Not existing type')
        response.status_code = 400
        return response
    body = r.text[1:-2]
    response = jsonify(body)
    response.status_code = 302
    return response


@app.route("/api/contacts/<uni>/<type>", methods=['GET'])
def get_contact_by_type_and_uni(uni, type):
    """ Note: here type can be phone, email or address
    response body be like
    [
        {
            "content": "1 3476290991",
            "id": 1,
            "name": "Di, Wu",
            "note": "mobile",
            "type": "phone",
            "uni": "dw3013"
        }
        {(contact2 of this type)}
        ......
    ]
    """
    if type == 'address' or type == 'email' or type == 'phone':
        if type == 'address':
            url = get_contacts_url() + "/api/contacts/" + uni + "/all_addresses"
        else:
            url = get_contacts_url() + "/api/contacts/" + uni + "/all_" + type + "s"
        content = requests.get(url).json()
        contact = ContactProcessing.processing(type, content)
    else:
        response = jsonify('Not existing type')
        response.status_code = 400
        return response

    response = jsonify(contact)
    response.status_code = 302
    return response


@app.route("/api/contacts/<type>", methods=['GET'])
def get_contact_by_type(type):
    """ Note: here type can be phone, email or address
    response body be like
    [
        {(contact1 of this type)},
        {(contact2 of this type)},
        ......
    ]
    """
    if type == 'address' or type == 'email' or type == 'phone':
        if type == 'address':
            url = get_contacts_url() + "/api/contacts/all_addresses"
        else:
            url = get_contacts_url() + "/api/contacts/all_" + type + "s"
        content = requests.get(url).json()
        contact = ContactProcessing.processing(type, content)
    else:
        response = jsonify('Not existing type')
        response.status_code = 400
        return response

    response = jsonify(contact)
    response.status_code = 302
    return response


@app.route("/api/contacts/<uni>", methods=['GET'])
def get_contact_by_uni(uni):
    """JSON response body be like
    [
        [(addresses)],
        [(phones)],
        [(emails)]
    ]
    """
    url =  get_contacts_url()+'/api/contacts/'+uni+'/all_contacts'
    content = requests.get(url).json()

    addr_list = ContactProcessing.address_processing(content[0])
    phone_list = ContactProcessing.phone_processing(content[1])
    email_list = ContactProcessing.email_processing(content[2])

    list = [addr_list, phone_list, email_list]

    response = jsonify(list)
    response.status_code = 302
    return response


@app.route("/api/contacts/all", methods=['GET'])
def all_contact():
    """JSON response body be like
    [
        [(addresses)],
        [(phones)],
        [(emails)]
    ]
    """
    url = get_contacts_url()+'/api/contacts/all_contacts'
    content = requests.get(url).json()

    addr_list = ContactProcessing.address_processing(content[0])
    phone_list = ContactProcessing.phone_processing(content[1])
    email_list = ContactProcessing.email_processing(content[2])

    list = [addr_list, phone_list, email_list]

    response = jsonify(list)
    response.status_code = 302
    return response


@app.route("/api/courses/new_session", methods=['POST'])
def add_a_new_session():
    pass


# Get or edit or delete a session
@app.route("/api/courses/<call_no>", methods=['GET', 'PUT', 'DELETE'])
def manipulate_a_session(call_no):
    pass


@app.route("/api/courses/<call_no>/new_project", methods=['POST'])
def add_a_new_project(call_no):
    pass


# Get or edit or delete a project
@app.route("/api/courses/<call_no>/projects/<project_id>", methods=['GET', 'PUT', 'DELETE'])
def manipulate_a_project(call_no, project_id):
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5011, ssl_context="adhoc")
