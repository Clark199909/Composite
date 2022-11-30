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


# Get all students’ info (uni, name, nationality, ethnicity, gender, admission date, section, project)
@app.route("/api/students/all_students", methods=['GET'])
def get_all_students_info():
    pass


# Create a student & Get & Edit & Delete a student's info
# POST: create a student and register the student to a course session
# GET: get a student's info (like fields in the all students info method)
# PUT: edit a student's info
# DELETE: delete a student (remember to delete the student record & students' contacts & change in projects
# ; if the project only has this one student, delete the whole project)
@app.route("/api/students/<uni>", methods=['POST', 'GET', 'PUT', 'DELETE'])
def manipulate_a_student(uni):
    pass


# Get student (general info/contact) by name/session call_no/project name/nationality/gender
# if info_type = "info", get students' fields (like above apis) according to the attribute
# if info_type = "contacts", get students' contacts fields (like below apis) according to the attribute
# attribute is name/session call_no/project name/nationality/gender
@app.route("/api/students/<info_type>/<attribute>")
def get_students_info_or_contact_by_attribute(info_type, attribute):
    pass

"""
example request body 1:
{
    "description": "home",
    "country": "USA",
    "state": "NY",
    "city": "NY",
    "zip_code": "10025",
    "street": "125W 109th St"
}
example request body 2:
{
    "description": "mobile",
    "country_code": "1",
    "phone_no": "3476290991"
}
example request body 3:
{
    "description": "personal",
    "address": "dw3013@columbia.edu"
}
"""

@app.route("/api/contacts/<uni>/add/<contact_type>", methods=['POST'])
@notification
def add_one_contact(uni, contact_type):
    data = request.json

    if contact_type == 'address':
        r = ContactResource.add_one_address(uni, body=data)
        response = jsonify(r.text)
        response.status_code = r.status_code
        return response
    elif contact_type == 'phone':
        r = ContactResource.add_one_phone(uni, body=data)
        response = jsonify(r.text)
        response.status_code = r.status_code
        return response
    elif contact_type == 'email':
        r = ContactResource.add_one_email(uni, body=data)
        response = jsonify(r.text)
        response.status_code = r.status_code
        return response
    else:
        response = jsonify('Incorrect type')
        response.status_code = 400
        return response


# fields include uni, first name, last name, type, note, content
# type means general type of contacts (email or address or phone?)
# note means specific type of one type of contact (e.g. mobile or home for phone contacts)
# content means contact info (e.g. country code + phone number for phone contacts)
@app.route("/api/contacts/all_students", methods=['GET'])
def get_all_contacts_of_all_students():
    pass


@app.route("/api/contacts/<uni>", methods=['GET'])
def get_all_contacts_of_a_student(uni):
    pass


@app.route("/api/contacts/<uni>/<type>/<note>", methods=['PUT', 'DELETE'])
def manipulate_a_contact(uni, type, note):
    pass


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
