"""Pushes the default First Day Information unit to a semester

The script will ensure the target course does not already have a First Day
Information unit before copying to it.

The template (copy-from) course Org Unit Id is 10646.

Provide the Otis Semester Code as command line argument 1.
"""

import csv
import sys

import datahub
import dwnld

DATA_PATH = "G:/Shared drives/~ LMS Brightspace Implementation/Data Hub"

def runner(idlist):
    """copies the First Day Information module to each course in idlist
    if it does not already exist
    """
    copylist = []
    for id in idlist:
        data = dwnld.get_toc(id)
        first_day = []
        for module in data['Modules']:
            if module['Title'] == 'First Day Information':
                first_day.append(module)
        if not first_day:
            copylist.append(id)
    if not copylist:
        print('No courses to copy to')

    for id in copylist:
        dwnld.course_copy(id, 10646, ['Content', 'CourseFiles'])

def mklist(semesterId):
    """Returns a list of course offering ids that are children of the semester
    and do not have a First Day Information module
    """
    children = dwnld.get_children(semesterId, ouTypeId=3)
    contentobjects = DATA_PATH + "/Data Sets/ContentObjects.csv"
    childlist = [i['Identifier'] for i in children]
    with open(contentobjects, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        firstdaylist = []
        for row in reader:
            if row['Title'] == 'First Day Information':
                firstdaylist.append(row['OrgUnitId'])
    idlist = [i for i in childlist if i not in firstdaylist]
    return idlist

if __name__ == "__main__":
    semesterId = datahub.get_orgunit(sys.argv[1])
    idlist = mklist(semesterId)
    runner(idlist)
