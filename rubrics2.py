"""Version 2 of a report on rubric assessments

optional argument '--bulk' + path to csv file to run reports for
multiple students
"""

import argparse
import os
import pandas as pd

import datahub
import dwnld
import report

def parse_args():
    """adds optional argument to run a bulk report"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--bulk', help='path to csv file with OrgUnitId and Xnumber columns')
    parser.add_argument('--ou', help='course offering org unit id number', type=int)
    parser.add_argument('--id', help='user org defined id')
    return parser.parse_args()

def build_report(ou, xid, rub_assess_df):
    """produces a rubric assessment report for one student in one course"""
    print(f'Starting report for {xid}')
    user = datahub.get_user(xid)
    course_code = datahub.get_code(ou)
    assessments = []
    rubrics = []
    df = rub_assess_df[rub_assess_df['UserId'] == int(user['UserId'])]
    grades = pd.read_csv(datahub.GRADE_OBJECTS)
    for r in df.itertuples():
        a = dwnld.get_rubric_assessment(r.OrgUnitId,r.ActivityType,r.ActivityObjectId,r.RubricId,r.UserId)
        try:  # add Grade Object Name to assessments if one exists
            if r.ActivityType == 'Grades':
                grade_item = grades.loc[grades['GradeObjectId'] == r.ActivityObjectId]
            else:
                grade_item = grades.loc[grades['AssociatedToolItemId'] == r.ActivityObjectId]
            a['GradeObjectName'] = grade_item.iloc[0,3]
        except:
            print('Grade object name not found')
        assessments.append(a)
        if r.RubricId not in [i['RubricId'] for i in rubrics if 'RubricId' in rubrics]:
            rubrics += dwnld.get_rubrics(r.OrgUnitId, r.ActivityType, r.ActivityObjectId)
    file = "{}_{}_{}_RubricAssessments.pdf".format(course_code, user['FirstName'], user['LastName'])
    filepath = os.path.join(datahub.REPORT_PATH, file)
    report.rubric_assessments(filepath, assessments, rubrics)
    print(f'Report for {xid} complete at {filepath}')

def main():
    """calls report() one or many times depending on args"""
    args = parse_args()
    df = pd.read_csv(datahub.RUBRIC_ASSESSMENT)
    if args.bulk:
        df2 = pd.read_csv(args.bulk)
        print(df2.head())
        df = df[df['OrgUnitId'].isin(df2['OrgUnitId'].unique())]
        for u in df2.itertuples():
            build_report(u.OrgUnitId, u.Xnumber, df)

    elif not args.bulk:
        ou = args.ou if args.ou else input('Enter course OrgUnitId: ')
        xid = args.id if args.id else input('Enter student X number: ')
        df = df[df['OrgUnitId'] == int(ou)]
        build_report(ou, xid, df)

    elif os.path.isfile(args.bulk) and args.bulk[-4] != '.csv':
        print('Please enter a valid path to your csv file with OrgUnitId and Xnumber columns')

if __name__ == '__main__':
    main()
