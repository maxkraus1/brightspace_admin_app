"""Provides a local web browser interface for executing scripts

Also provides an API endpoint to pull credentials into Postman
"""

import json
import os
import platform
import subprocess
from werkzeug.utils import secure_filename
from flask import Flask, flash, render_template, request, redirect
from flask_restful import Resource, Api, reqparse

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
api = Api(app)

call_py = 'python' if platform.system() == 'Windows' else 'python3'  # find cmd for python3

def allowed_file(filename):  # helper funtion for file uploads
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Credentials(Resource):  # to return credentials to Postman for testing
    def get(self):
        """returns the json data in credentials.json"""
        with open('scripts/records/credentials.json') as file:
            data = json.load(file)
            return data, 200

api.add_resource(Credentials, '/credentials')

def out_format(std_out):  # helper function to format shell output
    return [str(line, 'utf-8', 'ignore') for line in std_out.split(b'\r\n')]

@app.route('/')
def form():
    processes =['Semester Report',  # each process has a function below
                'Grades Report',
                'Grades Report Department',
                'Bulk Enroll Department Staff',
                'Rubrics Report',
                'Push First Day Info',
                'Download Evidence',
                'Download Syllabi',
                'Department Enrollment Report',
                'Update API credentials or paths',
                'Update Data Sets'
                ]
    return render_template('form.html', processes=sorted(processes))

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

@app.route('/syllabi/', methods=['POST'])
def syllabi():
    form_data = request.form
    args = [call_py, 'scripts/syllabi.py', form_data['SemesterCode'], form_data['Path']]
    if form_data['DepartmentCode'] != 'EXT':
        args += ['--dept', form_data['DepartmentCode']]
    sp = subprocess.run(args=args, capture_output=True)
    return render_template('data.html', form_data=form_data, out=out_format(sp.stdout))

@app.route('/dept_enrollment/', methods=['POST'])
def dept_enrollment():
    form_data = request.form
    args = [call_py, 'scripts/classlist.py', '--sem', form_data['SemesterCode'], '--dept', form_data['DepartmentCode']]
    sp = subprocess.run(args=args, capture_output=True)
    return render_template('data.html', form_data=form_data, out=out_format(sp.stdout))

@app.route('/update_data/', methods=['POST'])
def update_data():
    args = [call_py, 'scripts/data_update.py']
    sp = subprocess.run(args=args, capture_output=True)
    return render_template('data.html', form_data=None, out=out_format(sp.stdout))

@app.route('/update/', methods=['POST', 'GET'])
def update():
    """Handles displaying and updating paths and credentials JSON files"""
    # load json files
    paths_file = 'scripts/records/paths.json'
    creds_file = 'scripts/records/credentials.json'
    with open(paths_file) as infile:
        paths = json.load(infile)
    with open(creds_file) as infile:
        creds = json.load(infile)
    records = os.path.abspath('scripts/records')
    # display update template if GET request
    if request.method == 'GET':
        return render_template('update.html', paths=paths, credentials=creds, records=records)
    # update data if POST request
    elif request.method == 'POST':
        form_data = request.form
        key = form_data['selected']
        # update paths.json file if selected
        if key in paths.keys():
            paths[key] = form_data['newvalue']
            with open(paths_file, 'w') as outfile:
                json.dump(paths, outfile, indent=4)
        elif key in creds.keys():
            creds[key] = form_data['newvalue']
            with open(creds_file, 'w') as outfile:
                json.dump(creds, outfile, indent=4)
        return redirect('/update')


if __name__ == '__main__':
    import webbrowser
    webbrowser.open('http://localhost:5000')
    app.run(port=5000)
