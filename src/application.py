from flask import request, jsonify, redirect, url_for, current_app, session
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
    user_logged_out,
    COOKIE_NAME
)
import requests
import json

from src import app
from src.notification import notification
from src.smarty import verify_address
from src.resources.user_resource import UserResource
from src.models.user import User
from src import login_manager
from src import GOOGLE_DISCOVERY_URL
from src import GOOGLE_CLIENT_ID
from src import GOOGLE_CLIENT_SECRET
from src import client

from src.resources.students import StudentProcessing
from src.resources.contacts import ContactProcessing
from src.resources.courses import CourseResource

from src.config import get_courses_url
from src.config import get_students_url
from src.config import get_contacts_url



white_list = {"/", "/login", "/login/callback"}
FRONTEND_INDEX = "http://localhost:4200"
notification_block_list = {"/", "/login", "login/callback"}



# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    print(user_id)
    return User.get(user_id)


@app.before_request
def before_decorator():
    if request.path not in white_list:
        if "Uid" not in request.headers or not User.get(request.headers["Uid"]).is_authenticated:
            response = jsonify("User is not authenticated!")
            response.status_code = 400
            return response

# @app.after_request
# def after_decorator(response):
#     if request.path not in notification_block_list:
#         notification(response)
#     return response

@app.route("/")
def index():

    if "Uid" not in request.headers or not User.get(request.headers["Uid"]).is_authenticated:
        response = jsonify("User needs to log in.")
        response.status_code = 201
        return response

    response = jsonify("User is logged in.")
    response.status_code = 200
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

    response = jsonify(request_uri)
    response.status_code = 200
    return response


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

    url = FRONTEND_INDEX + "/?uid=" + unique_id
    return redirect(url)


@app.route("/logout")
# @login_required
def logout():
    user = User.get(request.headers["Uid"])
    custom_logout(user)

    response = jsonify("User is logged out.")
    response.status_code = 200
    return response


def custom_logout(user):
    if "_user_id" in session:
        session.pop("_user_id")

    if "_fresh" in session:
        session.pop("_fresh")

    if "_id" in session:
        session.pop("_id")

    cookie_name = current_app.config.get("REMEMBER_COOKIE_NAME", COOKIE_NAME)
    if cookie_name in request.cookies:
        session["_remember"] = "clear"
        if "_remember_seconds" in session:
            session.pop("_remember_seconds")

    user_logged_out.send(current_app._get_current_object(), user=user)

    current_app.login_manager._update_request_context_with_user()
    return True


@app.route("/api/students/add", methods=['POST'])
def add_new_student():
    """JSON copy to test
    {
        "uni": "ab1234",
        "first_name": "David",
        "last_name": "Martin",
        "nationality": "United States",
        "race": "White",
        "gender": "Male",
        "admission_date": "12/14/2022",
        "call_no": 1,
        "project_id":null
    }
    """
    data = request.json

    call_no = data['call_no']
    url_0 = get_students_url() + "/api/students/new_student"
    url_1 = get_contacts_url() + "/api/contacts/new_student"
    url_2 = get_courses_url() + f'/api/sections/{call_no}/new_student'

    r0 = requests.post(url_0, json=data)
    r1 = requests.post(url_1, json=data)
    r2 = requests.post(url_2, json=data)

    response = jsonify([r0.text[1:-2], r1.text[1:-2], r2.text[1:-2]])
    response.status_code = max(r0.status_code, r1.status_code, r2.status_code)
    return response


@app.route("/api/students/delete/<call_no>/<uni>", methods=['DELETE'])
def delete_a_student(call_no, uni):

    url_0 = get_students_url() + f'/api/students/del_student/{uni}'
    url_1 = get_contacts_url() + f'/api/contacts/del_student/{uni}'
    url_2 = get_courses_url() + f'/api/sections/{call_no}/students/{uni}'

    r0 = requests.delete(url_0)
    r1 = requests.delete(url_1)
    r2 = requests.delete(url_2)

    response = jsonify([r0.text[1:-2], r1.text[1:-2], r2.text[1:-2]])
    response.status_code = max(r0.status_code, r1.status_code, r2.status_code)
    return response


@app.route("/api/students/update/<uni>", methods=['PUT'])
def update_a_student(uni):
    """JSON copy to test
    {
        "first_name": "Daviiiid",
        "last_name": "Martin",
        "nationality": "United States",
        "race": "White",
        "gender": "Male",
        "admission_date": "12/14/2022",
        "call_no": 1,
        "project_id":null
    }
    """
    students_url = get_students_url() + f'/api/students/update_student/{uni}'
    courses_url = get_courses_url() + f'/api/enrollment/{uni}'
    data = request.json

    r1 = requests.put(students_url, json=data)
    r2 = requests.put(courses_url, json=data)

    response = jsonify([r1.text[1:-2], r2.text[1:-2]])
    response.status_code = max(r1.status_code, r2.status_code)
    return response


@app.route("/api/students/get/<uni>", methods=['GET'])
def get_student_by_uni(uni):
    """JSON response body be like
    [
        {
            "admission_date": "12/08/2022",
            "email": "dw3013@columbia.edu",
            "race": "Asian",
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
    response.status_code = 200
    return response


@app.route("/api/students/all", methods=['GET'])
def all_student():
    """JSON response be like
    [
        [{
            "uni": string,
            "name": string,
            "nationality": string,
            "race": string,
            "gender": string,
            "admission_date": string,
            "call_no": number,
            "project_id": number,
            "project_name": string,
            "team_name": string,
            "section_period": string
        }]
    ]
    """
    students_url = get_students_url() + "/api/students"
    courses_url = get_courses_url() + "/api/sections/students"
    students_content = requests.get(students_url).json()
    courses_content = requests.get(courses_url).json()
    info = StudentProcessing.processing(students_content, courses_content)
    response = jsonify(info)
    response.status_code = 200
    return response


@app.route("/api/courses/<call_no>/projects/<project_id>/available_students", methods=['GET'])
def get_all_students_in_one_section_available_for_a_project(call_no, project_id):
    """JSON response be like
        [
            [{
                "uni": string,
                "name": string,
                "nationality": string,
                "race": string,
                "gender": string,
                "admission_date": string,
                "call_no": number,
                "project_id": number,
                "project_name": string,
                "team_name": string,
                "section_period": string
            }]
        ]
        """
    students_url = get_students_url() + "/api/student_names"
    courses_url = get_courses_url() + f"/api/sections/{call_no}/students/no_project"
    all_student_names = requests.get(students_url).json()
    needed_unis = requests.get(courses_url).json()
    if int(project_id) > 0:
        url = get_courses_url() + f'/api/sections/{call_no}/projects/{project_id}/all_students'
        needed_unis = needed_unis + requests.get(url).json()
    needed_names_dict = StudentProcessing.get_names_of_students_with_no_project(all_student_names, needed_unis)
    response = jsonify(needed_names_dict)
    response.status_code = 200
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

        if type == 'address':
            check_passed, check_comment, correct_address = verify_address(data)
            if not check_passed:
                response = jsonify(f"address verification failed: {check_comment}")
                response.status_code = 400
                return response

            try:
                r = requests.post(url, json=correct_address)
            except:
                response = jsonify('Cannot connect to microservice')
                response.status_code = 500
                return response
        else:
            try:
                r = requests.post(url, json=data)
            except:
                response = jsonify('Cannot connect to microservice')
                response.status_code = 500
                return response
    else:
        response = jsonify('Not existing type')
        response.status_code = 400
        return response
    body = r.text[1:-2]

    if type == 'address':
        response = jsonify(body + f"; address verification result: {check_comment}")
    else:
        response = jsonify("Successfully added!")
    response.status_code = 200
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

        if type == 'address':
            check_passed, check_comment, correct_address = verify_address(data)
            if not check_passed:
                response = jsonify(f"address verification failed: {check_comment}")
                response.status_code = 400
                return response

            try:
                r = requests.put(url, json=correct_address)
            except:
                response = jsonify('Cannot connect to microservice')
                response.status_code = 500
                return response
        else:
            try:
                r = requests.post(url, json=data)
            except:
                response = jsonify('Cannot connect to microservice')
                response.status_code = 500
                return response
    else:
        response = jsonify('Not existing type')
        response.status_code = 400
        return response
    body = r.text[1:-2]

    if type == 'address':
        response = jsonify(body + f"; address verification result: {check_comment}")
    else:
        response = jsonify("Successfully updated!")
    response.status_code = 200
    return response


@app.route("/api/contacts/<uni>/del/<type>/<note>", methods=['DELETE'])
def delete_a_contact(uni, type, note):
    if type == 'address' or type == 'email' or type == 'phone':
        url = get_contacts_url() + "/api/contacts/" + uni + "/del_"+type + "/" + note
        r = requests.delete(url)
    else:
        response = jsonify('Not existing type')
        response.status_code = 400
        return response
    body = r.text[1:-2]
    response = jsonify(body)
    response.status_code = 200
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
    response.status_code = 200
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
    response.status_code = 200
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
    response.status_code = 200
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

    list = addr_list + phone_list + email_list

    response = jsonify(list)
    response.status_code = 200
    return response


@app.route("/api/courses/new_section", methods=['POST'])
def add_a_new_section():
    """
    request:
    {
        "call_no": number,
        "professor": string,
        "classroom": string,
        "year": number,
        "semester": string,
        "day": string,
        "start_hr": number,
        "start_min": number,
        "end_hr": number,
        "end_min": number,
        "section_type": string
    }
    """
    body = request.json
    r = CourseResource.add_new_section(body)

    response = jsonify(r.text[1:-2])
    response.status_code = r.status_code
    return response


@app.route("/api/courses/all_sections", methods=['GET'])
def get_all_sections():
    """
    response:
    {
        "call_no": number,
        "professor": string,
        "classroom": string,
        "year": number,
        "semester": string,
        "day": string,
        "start_hr": number,
        "start_min": number,
        "end_hr": number,
        "end_min": number,
        "section_type": string,
        "projects_num": number,
        "enrollments_num": number
    }
    """
    r = CourseResource.get_all_sections()
    response = jsonify(r.json())
    response.status_code = r.status_code
    return response


# Get or edit or delete a section
@app.route("/api/courses/<call_no>", methods=['PUT', 'DELETE'])
def manipulate_a_section(call_no):
    """
    For update request:
    {
        "call_no": number,
        "professor": string,
        "classroom": string,
        "year": number,
        "semester": string,
        "day": string,
        "start_hr": number,
        "start_min": number,
        "end_hr": number,
        "end_min": number,
        "section_type": string
    }
    """
    if request.method == 'DELETE':
        r = CourseResource.del_a_section(call_no)
        response = jsonify(r.text[1:-2])
        response.status_code = r.status_code
        return response
    else:
        body = request.json
        r = CourseResource.update_a_section(call_no, body)

        response = jsonify(r.text[1:-2])
        response.status_code = r.status_code
        return response


@app.route("/api/courses/<call_no>/new_project", methods=['POST'])
def add_a_new_project(call_no):
    """
    Request:
    {
        "project_name": string,
        "team_name": string,
        "project_members": string[]
    }
    """
    body = request.json
    r = CourseResource.add_new_project(call_no, body)

    response = jsonify(r.text[1:-2])
    response.status_code = r.status_code
    return response


@app.route("/api/courses/all_projects", methods=['GET'])
def get_all_projects():
    """
    Response:
    [
        {
            "call_no": number;
            "id": number;
            "project_name": string;
            "team_name": string;
            "project_members": string[];
            "section_period": string;
        }
    ]
    """
    r = CourseResource.get_all_projects()
    response = jsonify(r.json())
    response.status_code = r.status_code
    return response


# Get or edit or delete a project
@app.route("/api/courses/<call_no>/projects/<project_id>", methods=['PUT', 'DELETE'])
def manipulate_a_project(call_no, project_id):
    """
    For update request:
    {
        "project_name": string,
        "team_name": string,
        "project_members": string[]
    }
    """
    if request.method == 'DELETE':
        r = CourseResource.del_a_project(project_id)
        response = jsonify(r.text[1:-2])
        response.status_code = r.status_code
        return response
    else:
        body = request.json
        r = CourseResource.update_a_project(call_no, project_id, body)

        response = jsonify(r.text[1:-2])
        response.status_code = r.status_code
        return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5011, ssl_context="adhoc")

