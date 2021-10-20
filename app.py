"""Provides an API endpoint at the localhost for communication with Postman"""

import json

from flask import Flask
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

class Credentials(Resource):
    def get(self):
        """returns the json data in credentials.json"""
        with open('credentials.json') as file:
            data = json.load(file)
            return data, 200

api.add_resource(Credentials, '/credentials')

if __name__ == '__main__':
    app.run()
