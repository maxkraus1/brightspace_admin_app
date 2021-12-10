"""Enrolls a user in all courses in a department where they are not enrolled"""

import argparse
import os
import pandas as pd

import datahub
import dwnld

parser = argparse.ArgumentParser()
parser.add_argument('dept', type=str, help='department code')
parser.add_argument('sem', type=int, help='semester code')
parser.add_argument('id', type=str, help='user id (LMS Org Defined Id)')
parser.add_argument('--role', type=str, help='role id (default is 122 for Department Staff)')
args = parser.parse_args()

user = datahub.get_user(args.id)

semester_report = os.path.join( datahub.REPORT_PATH,
                                "Semester Course Reports",
                                "{}_SemesterReport.xlsx".format(args.sem))

df = pd.read_excel(semester_report)
df = df[df['DeptCode'] == args.dept]
df = df[df['InstructorXnumber'].str.contains(args.id) == False]
df.dropna(subset=['InstructorXnumber'], inplace=True)

if args.role:
    role = args.role  # if role argument is supplied, assign to variable
else:
    role = 122  # default role is Department Staff

for ou in df['OrgUnitId'].to_list():
    dwnld.enroll(ou, user['UserId'], role)
