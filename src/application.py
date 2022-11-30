from flask import request, jsonify
from src import app

from src.resources.contacts import ContactResource
from src.resources.notification import notification

"""
example request body 1:
{
    "type": "address",
    "data": {
        "description": "home",
        "country": "USA",
        "state": "NY",
        "city": "NY",
        "zip_code": "10025",
        "street": "125W 109th St"
    }
}
example request body 2:
{
    "type": "phone",
    "data": {
        "description": "mobile",
        "country_code": "1",
        "phone_no": "3476290991"
    }
}
example request body 3:
{
    "type": "email",
    "data": {
        "description": "personal",
        "address": "dw3013@columbia.edu"
    }
}
"""
@app.route("/api/contacts/<uni>/add", methods=['POST'])
@notification
def add_one_contact(uni):
    data = request.json
    if 'type' not in data or 'data' not in data:
        response = jsonify('Incomplete request body')
        response.status_code = 400
        return response

    if data['type'] == 'address':
        r = ContactResource.add_one_address(uni, body=data['data'])
        response = jsonify(r.text)
        response.status_code = r.status_code
        return response
    elif data['type'] == 'phone':
        r = ContactResource.add_one_phone(uni, body=data['data'])
        response = jsonify(r.text)
        response.status_code = r.status_code
        return response
    elif data['type'] == 'email':
        r = ContactResource.add_one_email(uni, body=data['data'])
        response = jsonify(r.text)
        response.status_code = r.status_code
        return response
    else:
        response = jsonify('Incorrect type')
        response.status_code = 400
        return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5011)
