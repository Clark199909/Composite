from typing import Dict
import requests
from src.config import get_contacts_url

class ContactResource:
    def __int__(self):
        pass

    @staticmethod
    def add_one_address(uni: str, body: Dict):
        url = get_contacts_url() + f'/api/contacts/{uni}/new_address'
        return requests.post(url = url, json = body)

    @staticmethod
    def add_one_phone(uni: str, body: Dict):
        url = get_contacts_url() + f'/api/contacts/{uni}/new_phone'
        return requests.post(url = url, json= body)

    @staticmethod
    def add_one_email(uni: str, body: Dict):
        url = get_contacts_url() + f'/api/contacts/{uni}/new_email'
        return requests.post(url = url, json = body)
