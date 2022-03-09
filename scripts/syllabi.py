"""Downloads syllabi files to a specified path"""

import argparse
import os
import re

import pandas as pd

import dwnld
from datahub import REPORT_PATH

parser = argparse.ArgumentParser()
parser.add_argument("semester", help="School semester code i.e. '202130'")
parser.add_argument("destination", help="path to folder for syllabi")
parser.add_argument("--dept", help="School Department code to select only those courses", type=str)
parser.add_argument("--csv", help="csv file with OrgUnitId and Name for each course", type=str)
args = parser.parse_args()

if args.csv:  # get courses from supplied csv file
    df = pd.read_csv(args.csv)
else:  # get courses from semester report
    sem_report = os.path.join(REPORT_PATH, "Semester Course Reports", args.semester + "_SemesterReport.xlsx")
    df = pd.read_excel(sem_report)
    df = df[df['StudentCount'] > 0]
    df.dropna(subset=['InstructorEmail'], inplace=True)
if args.dept:  # filter semester report courses by department
    df = df[df['DeptCode'] == args.dept]

# iterate through df and download syllabi
for index, course in df.iterrows():
    try:
        toc = dwnld.get_toc(course['OrgUnitId'])
        classlist = dwnld.get_classlist(course['OrgUnitId'])
        lastnames = [u['LastName'] for u in classlist if u['RoleId'] == 109]

        try:
            module = next(m for m in toc['Modules'] if "syllabus" in m['Title'].lower() and m['IsHidden'] == False)
            if len(module['Description']["Html"]) > 50:
                description = os.path.join( args.destination,
                                            "{}_{}_{}".format(  re.sub(r'[^\d\w \-_]+', '_', course['Name']),
                                                                '_'.join(lastnames),
                                                                "0.html")
                                            )
                with open(description, "w") as outfile:
                    outfile.write(module['Description']["Html"])
            count = 1
            for topic in [t for t in module['Topics'] if t['ActivityType'] == 1 and t['IsHidden'] == False]:
                filename = "{}_{}_{}_{}".format(re.sub(r'[^\d\w \-_]+', '_', course['Name']),
                                                '_'.join(lastnames),
                                                count,
                                                os.path.basename(topic['Url']))
                filepath = os.path.join(args.destination, filename)
                url = dwnld.DOMAIN + '/le/{}/{}/content/topics/{}/file'.format( dwnld.LE_VERSION,
                                                                                course['OrgUnitId'],
                                                                                topic['TopicId'])
                dwnld.get_file_url(url, filepath)
                count += 1
        except StopIteration as e:
            print('No Syllabus: {} {}'.format(course['Name'], course['OrgUnitId']))
            print(e)
    except:
        print("Skipping org unit not found: ", course['OrgUnitId'])
