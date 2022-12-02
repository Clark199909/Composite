from flask import request, jsonify
from src import app
import requests
from src.resources.students import StudentProcessing
from src.resources.contacts import ContactProcessing

COURSE_URL = "http://0.0.0.0:5011"
CONTACT_URL = "http://0.0.0.0:5012"
STUDENT_URL = "http://0.0.0.0:5013"

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

    url_0 = STUDENT_URL + "/api/students/new_student"
    url_1 = CONTACT_URL + "/api/contacts/new_student"

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

    url_0 = STUDENT_URL + "/api/students/del_student"
    url_1 = CONTACT_URL + "/api/contacts/del_student"

    r_list = []
    r_list.append(requests.post(url_0, json=data).text[1:-2])
    r_list.append(requests.post(url_1, json=data).text[1:-2])

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
    url = STUDENT_URL + "/api/students/update_student"
    data = request.json
    r = requests.post(url, json=data)
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
    url = STUDENT_URL + "/api/students/" + uni
    content = requests.get(url).json()
    info = StudentProcessing.processing(content)
    response = jsonify(info)
    response.status_code = 302
    return response


@app.route("/api/students/all", methods=['GET'])
def all_student():
    """JSON respone be like
    [
        {(student info 1)},
        {(student info 2)}
    ]
    Note: if a student do not have email, his/her email will be like { email: '' }
    """
    url = STUDENT_URL + "/api/students"
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
        url = CONTACT_URL + "/api/contacts/" + uni + "/new_"+type
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
        url = CONTACT_URL + "/api/contacts/" + uni + "/update_"+type
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
        url = CONTACT_URL + "/api/contacts/" + uni + "/del_"+type
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
            url = CONTACT_URL + "/api/contacts/" + uni + "/all_addresses"
        else:
            url = CONTACT_URL + "/api/contacts/" + uni + "/all_" + type + "s"
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
            url = CONTACT_URL + "/api/contacts/all_addresses"
        else:
            url = CONTACT_URL + "/api/contacts/all_" + type + "s"
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
    url = CONTACT_URL+'/api/contacts/'+uni+'/all_contacts'
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
    url = CONTACT_URL+'/api/contacts/all_contacts'
    content = requests.get(url).json()

    addr_list = ContactProcessing.address_processing(content[0])
    phone_list = ContactProcessing.phone_processing(content[1])
    email_list = ContactProcessing.email_processing(content[2])

    list = [addr_list, phone_list, email_list]

    response = jsonify(list)
    response.status_code = 302
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5014)