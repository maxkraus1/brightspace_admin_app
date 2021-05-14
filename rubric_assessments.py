"""Produces pdf reports of rubric assessments for each student from Grades

Provide a csv file as with columns [OrgUnitId, Xnumber] as command line
argument 1
"""

import csv
import os
import sys

import datahub
import dwnld
import report

def get_org_data(orgUnitId):
    """returns list of rubric objects and grade-rubric grade id pairs"""
    grade_objects = datahub.get_grade_objects(orgUnitId)
    exclude = ['Category', 'Final Adjusted', 'Final Calculated', 'Calculated']
    gradeIds = []
    for g in grade_objects:
        if g['TypeName'] not in exclude:
            gradeIds.append(g['GradeObjectId'])
    rubrics = []
    id_pairs = []
    for id in gradeIds:
        try:
            r_list = dwnld.get_rubrics(orgUnitId, 'Grades', id)
            for rubric in r_list:
                rubrics.append(rubric)
                id_pairs.append({'objectId': id,
                                'rubricId': rubric['RubricId']})
        except:
            print("No rubric for gradeId({})".format(id))
            continue
    return {'rubrics': rubrics, 'id_pairs': id_pairs}


def rubrics_report(orgUnitId, rubrics, id_pairs, userId, filename):
    """generates a report on all graded rubrics for a user in a course"""
    if filename[-4:] != ".pdf":
        filename += ".pdf"  # handle errors with file extension
    grades_data = dwnld.get_grades_values(orgUnitId, userId)
    assessments = []
    for i in id_pairs:
        try:
            assessment = dwnld.get_rubric_assessment(orgUnitId,
                                            'Grades',
                                            i['objectId'],
                                            i['rubricId'],
                                            userId)
            assessments.append(assessment)
        except:
            logging.warning(
                "No assessment for gradeId({})".format(i['objectId']))
            continue
    if assessments:
        report.rubric_assessments(filename, assessments, rubrics)
    else:
        raise ValueError('No Assessments')

def main():
    with open(sys.argv[1], newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        org_data_bank = {}
        for line in reader:
            student = datahub.get_user(line["Xnumber"])
            userid = student["UserId"]
            course_code = datahub.get_code(line["OrgUnitId"])
            filename = "{}_{}_{}_RubricAssessments.pdf".format(course_code,
                                                           student["FirstName"],
                                                           student["LastName"])
            filepath = os.path.join(datahub.REPORT_PATH, filename)
            orgUnitId = line['OrgUnitId']
            if orgUnitId not in org_data_bank.keys():
                org_data = get_org_data(orgUnitId)
                org_data_bank[orgUnitId] = org_data
            else:
                org_data = org_data_bank[orgUnitId]
            rubrics = org_data['rubrics']
            id_pairs = org_data['id_pairs']
            rubrics_report(orgUnitId, rubrics, id_pairs, userid, filepath)

main()
