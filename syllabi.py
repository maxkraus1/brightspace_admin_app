"""Downloads syllabi files to a specified path"""

import argparse
import os
import re

import pandas as pd

import dwnld

parser = argparse.ArgumentParser()
parser.add_argument("courses", help="csv file with OrgUnitId and Name for each course")
parser.add_argument("destination", help="path to folder for syllabi")
args = parser.parse_args()

df = pd.read_csv(args.courses)

for index, course in df.iterrows():
    toc = dwnld.get_toc(course['OrgUnitId'])
    classlist = dwnld.get_classlist(course['OrgUnitId'])
    lastnames = [u['LastName'] for u in classlist if u['RoleId'] == 109]
    module = next(m for m in toc['Modules'] if "syllabus" in m['Title'].lower())
    for topic in [t for t in module['Topics'] if t['ActivityType'] == 1]:
        #try:
        filename = re.sub(r'[^\d\w \-_]+', '_', course['Name']) + '_' + '_'.join(lastnames) + '_' + os.path.basename(topic['Url'])
        filepath = os.path.join(args.destination, filename)
        if topic['Url'][-4:] == 'html':
            url = dwnld.DOMAIN + '/le/{}/{}/content/topics/{}/file'.format(dwnld.LE_VERSION, course['OrgUnitId'], topic['TopicId'])
        else:
            url = 'https://lms.otis.edu' + topic['Url']
        dwnld.get_file_url(url, filepath)
        """except:
            print("FAILED DOWNLOAD: {}".format(course['OrgUnitId']))
            continue"""
