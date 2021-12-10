"""Provides a local web browser interface for executing scripts

Also provides an API endpoint to pull credentials into Postman
"""

import json
import os
import subprocess

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

def out_format(std_out):  # helper function to format shell output
    return [str(line, 'utf-8', 'ignore') for line in std_out.split(b'\r\n')]

@app.route('/')
def form():
    processes =['Semester Report',
                'Grades Report',
                'Bulk Enroll Department Staff',
                'Rubrics Report',
                'Push First Day Info']
    return render_template('form.html', processes=processes)

@app.route('/data/', methods = ['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/' to submit form"
    if request.method == 'POST':
        form_data = request.form
        args = ['python',  'semester_report.py', form_data['SemesterCode']]
        sp = subprocess.run(args=args, capture_output=True)
        return render_template('data.html',form_data=form_data, out=out_format(sp.stdout))

@app.route('/grades_report/', methods=['POST'])
def grades_report():
    form_data = request.form
    os.system('python grades_report.py --org {}'.format(form_data['OrgUnitId']))
    return render_template('data.html',form_data = form_data)

@app.route('/bulk_enroll/', methods=['POST'])
def bulk_enroll():
    form_data = request.form
    args = ['python', 'bulk_enroll_dept.py', form_data['Department'], form_data['Semester'], form_data['UserId']]
    sp = subprocess.run(args=args, capture_output=True)
    return render_template('data.html', form_data=form_data, out=out_format(sp.stdout))

@app.route('/rubrics/', methods=['POST'])
def rubrics():
    form_data = request.form
    args = ['python', 'rubrics2.py', '--ou', form_data['OrgUnitId'], '--id',form_data['UserId']]
    sp = subprocess.run(args=args, capture_output=True)
    return render_template('data.html', form_data=form_data, out=out_format(sp.stdout))

@app.route('/firstday/', methods=['POST'])
def firstday():
    form_data = request.form
    args = ['python', 'firstday.py', form_data['SemesterCode'], '--nocheck']
    sp = subprocess.run(args=args, capture_output=True)
    return render_template('data.html', form_data=form_data, out=out_format(sp.stdout))

if __name__ == '__main__':
    # import webbrowser
    # webbrowser.open('http://localhost:5000')
    app.run(port=5000)
