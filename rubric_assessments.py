"""Produces pdf reports of rubric assessments for each student from Grades

Provide a csv file as with columns [OrgUnitId, Xnumber] as command line
argument 1
"""

import csv
import os
import sys

import dwnld

# import datahub module from the DataHub directory,
# which should be next to APiscripts directory
dh_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "DataHub")
sys.path.insert(1, dh_path)
import datahub



report_path="G:/Shared drives/~ LMS Brightspace Implementation/Data Hub/Reports"

with open(sys.argv[1], newline="", encoding="utf-8-sig") as csvfile:
    reader = csv.DictReader(csvfile)
    for line in reader:
        student = datahub.get_user(line["Xnumber"])
        userid = student["UserId"]
        course_code = datahub.get_code(line["OrgUnitId"])
        filename = "{}_{}_{}_RubricAssessments.pdf".format(course_code,
                                                           student["FirstName"],
                                                           student["LastName"])
        filepath = os.path.join(report_path, filename)
        dwnld.rubrics_report(line["OrgUnitId"], userid, filepath)
