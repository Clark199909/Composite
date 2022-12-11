import requests
from src.config import get_courses_url


class CourseResource:
    def __int__(self):
        pass

    @staticmethod
    def add_new_section(body):
        url = get_courses_url() + "/api/sections/new_section"
        response = requests.post(url, json=body)
        return response

    @staticmethod
    def get_all_sections():
        url = get_courses_url() + "/api/sections"
        response = requests.get(url)
        return response

    @staticmethod
    def add_new_project(call_no, body):
        url = get_courses_url() + f'/api/sections/{call_no}/new_project'
        response = requests.post(url, json=body)
        return response

    @staticmethod
    def del_a_section(call_no):
        url = get_courses_url() + f'/api/sections/{call_no}'
        response = requests.delete(url)
        return response

    @staticmethod
    def update_a_section(call_no, body):
        url = get_courses_url() + f'/api/sections/{call_no}'
        response = requests.put(url, json=body)
        return response

    @staticmethod
    def get_all_projects():
        url = get_courses_url() + "/api/sections/all_projects"
        response = requests.get(url)
        return response

    @staticmethod
    def del_a_project(project_id):
        url = get_courses_url() + f'/api/sections/delete_project/{project_id}'
        response = requests.delete(url)
        return response

    @staticmethod
    def update_a_project(project_id, body):
        url = get_courses_url() + f'/api/sections/update_project/{project_id}'
        response = requests.put(url, json=body)
        return response
