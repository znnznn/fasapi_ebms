import json
from base64 import b64encode

import requests

from settings import EBMS_API_PASSWORD, EBMS_API_LOGIN, EBMS_API_URL


class BasicAUTHRequest:
    password = EBMS_API_PASSWORD
    login = EBMS_API_LOGIN
    ebms_host = EBMS_API_URL

    @staticmethod
    def get_session():
        return requests.Session()

    def add_default_headers(self, headers=None):
        headers = headers or {}
        return {
            "Authorization": self.get_auth_token(self.login, self.password),
            "Content-Type": "application/json",
            "Accept": "*/*",
            **headers
        }

    @staticmethod
    def get_auth_token(username, password):
        token = b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
        return f'Basic {token}'

    def get(self, url, headers=None):
        with self.get_session() as session:
            return session.get(url, headers=self.add_default_headers(headers))

    def post(self, url, data=None, headers=None):
        with self.get_session() as session:
            return session.post(url, data=json.dumps(data), headers=self.add_default_headers(headers))

    def put(self, url, data=None, headers=None):
        with self.get_session() as session:
            return session.put(url, data=json.dumps(data), headers=self.add_default_headers(headers))

    def delete(self, url, headers=None):
        with self.get_session() as session:
            return session.delete(url, headers=self.add_default_headers(headers))

    def patch(self, url, data=None, headers=None):
        print(data)
        with self.get_session() as session:
            return session.patch(url, data=json.dumps(data), headers=self.add_default_headers(headers))


class ArinvClient(BasicAUTHRequest):
    ebms_model: str = "ARINV"
    select: str = "AUTOID,SHIP_DATE"

    def retrieve_url(self, autoid):
        print(f"{self.ebms_host}/{self.ebms_model}('{autoid}')?$select='{self.select}'")
        return f"{self.ebms_host}/{self.ebms_model}('{autoid}')?$select={self.select}"
