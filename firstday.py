"""Pushes the default First Day Information unit to a semester

The script will ensure the target course does not already have a First Day
Information unit before copying to it.

The template (copy-from) course Org Unit Id is 10646.

Provide the Otis Semester Code as command line argument 1.
"""

import argparse
import csv
import sys

import datahub
import dwnld

DATA_PATH = "G:/Shared drives/~ LMS Brightspace Implementation/Data Hub"
sourceId = 10646

parser = argparse.ArgumentParser()
parser.add_argument('semester', help="Otis semester code (i.e. '202210')")
parser.add_argument('--nocheck', action='store_true', help='Prevents input for user to confirm before copying')
args = parser.parse_args()

def runner(idlist):
    """copies the First Day Information module to each course in idlist
    if it does not already exist
    """
    copylist = []
    for id in idlist:
        data = dwnld.get_toc(id)
        first_day = []
        for module in data['Modules']:
            if 'First Day Information' in module['Title']:
                first_day.append(module)
        if not first_day:
            copylist.append(id)
    if copylist:
        print("There are {} courses without a First Day Information Unit".format(len(copylist)))
        copy = 'y' if args.nocheck else input("Would you like to copy? (Y/N): ")
        if copy.lower() in ("y", "yes"):
            for id in copylist:
                dwnld.course_copy(id, sourceId, ['Content', 'CourseFiles'])
        else:
            print("copy aborted")
    else:
        print("No courses to copy to")

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
            if 'First Day Information' in row['Title']:
                firstdaylist.append(row['OrgUnitId'])
    idlist = []
    for i in childlist:
        if i not in firstdaylist:
            # status = dwnld.get_copy_logs({"sourceOrgUnitId": sourceId,"destinationOrgUnitId": i})
            # if status == 404: # make sure default was not deleted by instructor
            idlist.append(i)
    return idlist

if __name__ == "__main__":
    semesterId = datahub.get_orgunit(args.semester)
    idlist = mklist(semesterId)
    runner(idlist)
