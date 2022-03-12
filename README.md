# Brightspace Admin App
This project is intended for administrators of a D2L Brightspace LMS instance and provides various bulk processes and automation, such as
* pushing content to all courses in a semester
* downloading all final project submissions and assessments from a selection of courses (department/semester)
* creating reports from system data
* and more!

The processes can be run via the browser-based UI by running ```app.py```, or from the command line in the /scripts directory.

*Note: terms or processes that are specific to the original developer's Brightspace instance may be embedded in the code. It is encouraged for Brightspace admins to adapt the code in this project to their own specific needs.*


## Installation
Make sure Python 3.9.1 or later is installed on your system.

Download and extract the code to a directory on your computer, or use
```bash
git clone https://github.com/maxkraus1/brightspace_admin_app.git
```
Go to the project directory:
```bash
cd brightspace_admin_app/
```
Install the required packages:
```bash
pip3 install -r requirements.txt
```
To launch the browser-based app:
```bash
python3 app.py
```
## Brightspace API Setup
Follow the directions in [Learn Postman with Paul](https://community.brightspace.com/s/article/Learn-Postman-with-Paul) to set up your OAuth2.0 app in Brightspace and obtain your initial access token and refresh token. Set the scope of your app in Brightspace to:
```
content:file:read content:modules:read,write content:toc:read content:topics:read,write core:*:* datahub:dataexports:download,read enrollment:orgunit:create import:job:create,fetch users:userdata:create
```
## Define Paths and API credentials
* From the browser UI, select the “Update API credentials and paths” option
* Select the “Update Data Paths” option. Set the DataPath to where you want data sets to be stored, and the ReportPath to where reports should be stored.
* Select the "Update OAuth 2.0 Credentials" option. Copy your initial access token and refresh token from Postman (see [Learn Postman with Paul](https://community.brightspace.com/s/article/Learn-Postman-with-Paul)), your client id and client secret from Brightspace, and set the values for each.

## Schedule Data Set Updates
Using task scheduler on Windows or a cron job on Linux/MacOs, schedule the following script to execute daily for some time after your daily Brightspace data sets update:
```
python3 scripts/data_update.py
```
## Features
* Bulk enroll a user in all department courses, skipping the ones they teach or that do not have students enrolled (for department chairs + staff).
* Copy content from a template course to all courses in a department
* Download all Assignment submissions and assessments that match a certain keyword (i.e. "final project")
* Download all syllabi from courses in a department and/or semester
* Produce a report on all rubric assessments for a student in a given class
* Produce a report on enrolled users in a group of courses or entire department
* Produce a report on grades for all courses in a department or a single course
* Produce a report on all courses in a semester that includes a count of students enrolled, faculty emails, # of pages in Content, and more
* Download most recent full data set and perform an upsert of any recent differential data sets
* Look up the courses that two or more users are enrolled in
* Bulk update course offering info (name, start/end dates, etc.)

## Project Structure
* app.py is the main script to access most functionality via the browser-based UI
  * scripts/auth.py handles authentication and refreshing the API tokens
  * scripts/dwnld.py houses all of the HTTP request methods
  * scripts/datahub.py houses all of the data set operation methods
  * scripts/report.py houses the PDF report methods using the reportlab library
  * all other .py files in the scripts/ directory run their own processes
* The scripts/records directory holds the configuration files paths.json, credentials.json, and datasets.json, as well as the dwnld_debug.log file.
* The templates/ directory holds the html templates and the static/ directory holds the static files used by app.py

## Command line usage
While all processes can be run from the browser based UI, scripts can also be executed directly from the command line with more optional arguments.
### Bulk Enroll Department staff
Example:
```bash
python3 scripts/bulk_enroll_dept.py [DepartmentCode] [SemesterCode] [OrgDefinedId]
```
The default RoleId is 122 (for Department Staff), but can be changed with optional argument:
```bash
--role [RoleId]
```
### Department Enrollment Report
#### OPTION 1 : Excel file with each course on its own tab
For all courses:
```
python3 scripts/classlist.py --sem [SemesterCode] --dept [DepartmentCode]
```
OR for a selection of courses:
```
python3 scripts/classlist.py --csv [path to csv file]
```
*csv file should have “OrgUnitId”, “Name”, and “Code” as columns*

#### OPTION 2: CSV file with one row per enrollment
Able to choose either faculty or student enrollments.
```
python3 scripts/enrollment_lookup.py  
```
Follow the prompts for inputs.

### Download Assignment Submissions and Assessments
Choose a keyword, such as "final project" to filter assignment titles that will be included in the download. The CSV file should have "OrgUnitId", "Name", "Code", and "Path" columns with a row for each course. Define the path to each parent folder inside which the script will create a sub folder for the course downloads.
```
python3 evidence.py [keyword to search] [path to csv file]
```
### Push Content to All Courses in a Semester
Open scripts/firstday.py in a text editor and change the ```sourceId``` variable to the OrgUnitId of your template course you want to copy content FROM.<br>
By default, it will not copy to courses that it has copied to before or that already have a “First Day Information” unit.
```
python3 firstday.py [SemesterCode]
```
#### Optional Arguments
* To suppress the confirmation check ("do you want to copy Y/N"), add ```--nocheck```
* To suppress the check for any past copies to a course add ```--nopast```

### Rubric Assessment Report
```
python3 rubrics2.py --id [OrgDefinedId] --ou [OrgUnitId]
```

### Semester Course Report
This process will create an Excel file in the "Semester Course Reports" folder within the "ReportPath" defined in scripts/records/paths.json. This can be used to find appropriate course codes for bulk user uploads, as well as other reports.
```
python3 semester_report.py [SemesterCode]
```

### Syllabi Collection
This process will download the unit description and all of the files in the first unit in a course with “Syllabus” in its title to the specified destination path
```
python3 syllabi.py [SemesterCode] [path to parent folder] --dept [DepartmentCode]
```
### User Enrollment Lookup

```
python3 users_lookup.py [OrgDefinedId 1] [OrgDefinedId 2] ...
```

## License
#### The code in this project is licensed under MIT license.
Copyright (c) 2022 Max Kraus

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
