"""Provides an API endpoint at the localhost for communication with Postman"""

import json
import os

from flask import Flask, render_template, request
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

@app.route('/')
def form():
    processes = ['Semester Report', 'Grades Report']
    return render_template('form.html', processes=processes)

@app.route('/data/', methods = ['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/' to submit form"
    if request.method == 'POST':
        form_data = request.form
        os.system('python semester_report.py {}'.format(form_data['SemesterCode']))
        return render_template('data.html',form_data = form_data)

@app.route('/grades_report/', methods=['POST'])
def grades_report():
    form_data = request.form
    os.system('python grades_report.py --org {}'.format(form_data['OrgUnitId']))
    return render_template('data.html',form_data = form_data)

if __name__ == '__main__':
    # import webbrowser
    # webbrowser.open('http://localhost:5000')
    app.run(port=5000)
