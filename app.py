"""Provides a local web browser interface for executing scripts

Also provides an API endpoint to pull credentials into Postman
"""

import json
import os
import platform
import subprocess
from werkzeug.utils import secure_filename
from flask import Flask, flash, render_template, request
from flask_restful import Resource, Api, reqparse

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
api = Api(app)

call_py = 'py' if platform.system() == 'Windows' else 'python3'  # find cmd for python3

def allowed_file(filename):  # helper funtion for file uploads
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
                'Grades Report Department',
                'Bulk Enroll Department Staff',
                'Rubrics Report',
                'Push First Day Info',
                'Download Evidence'
                ]
    return render_template('form.html', processes=processes)

@app.route('/data/', methods = ['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/' to submit form"
    if request.method == 'POST':
        form_data = request.form
        args = [call_py,  'scripts/semester_report.py', form_data['SemesterCode']]
        sp = subprocess.run(args=args, capture_output=True)
        return render_template('data.html',form_data=form_data, out=out_format(sp.stdout))

@app.route('/grades_report/', methods=['POST'])
def grades_report():
    form_data = request.form
    args = [call_py, 'scripts/grades_report.py', '--org', form_data['OrgUnitId']]
    sp = subprocess.run(args=args, capture_output=True)
    return render_template('data.html',form_data = form_data, out=out_format(sp.stdout))

@app.route('/grades_report_dept/', methods=['POST'])
def grades_report_dept():
    form_data = request.form
    args = [call_py, 'scripts/grades_report.py', '--dept', form_data['DepartmentCode'], form_data['SemesterCode']]
    sp = subprocess.run(args=args, capture_output=True)
    return render_template('data.html',form_data = form_data, out=out_format(sp.stdout))

@app.route('/bulk_enroll/', methods=['POST'])
def bulk_enroll():
    form_data = request.form
    args = [call_py, 'scripts/bulk_enroll_dept.py', form_data['Department'], form_data['Semester'], form_data['UserId']]
    sp = subprocess.run(args=args, capture_output=True)
    return render_template('data.html', form_data=form_data, out=out_format(sp.stdout))

@app.route('/rubrics/', methods=['POST'])
def rubrics():
    form_data = request.form
    args = [call_py, 'scripts/rubrics2.py', '--ou', form_data['OrgUnitId'], '--id',form_data['UserId']]
    sp = subprocess.run(args=args, capture_output=True)
    return render_template('data.html', form_data=form_data, out=out_format(sp.stdout))

@app.route('/firstday/', methods=['POST'])
def firstday():
    form_data = request.form
    args = [call_py, 'scripts/firstday.py', form_data['SemesterCode'], '--nocheck']
    sp = subprocess.run(args=args, capture_output=True)
    return render_template('data.html', form_data=form_data, out=out_format(sp.stdout))

@app.route('/evidence/', methods=['POST'])
def evidence():
    form_data = request.form
    file = request.files['csvfile']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    args = [call_py, 'scripts/evidence.py', form_data['keyphrase'], filepath]
    sp = subprocess.run(args=args, capture_output=True)
    return render_template('data.html', form_data=form_data, out=out_format(sp.stdout))

if __name__ == '__main__':
    # import webbrowser
    # webbrowser.open('http://localhost:5000')
    app.run(port=5000)
