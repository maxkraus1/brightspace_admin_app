"""Outputs Excel report with grades values for each courses in a department"""

import argparse
from operator import itemgetter
import os
import pandas as pd

import datahub
import dwnld
import report

# dept_code = input("Enter department code: ")
# sem_code = input("Enter semester code: ")
# dept_ou = datahub.get_orgunit(dept_code)
# sem_ou = datahub.get_orgunit(sem_code)
# course_org_units = datahub.get_descendants(dept_ou, sem_ou)
# report_path = os.path.join(datahub.REPORT_PATH, dept_code, sem_code)
ou = 12092
course_info = dwnld.get_course_info(ou)
classlist = sorted([u for u in dwnld.get_classlist(ou) if u['RoleId'] == 110],
                    key=itemgetter('DisplayName'))

def excel_report():
    df = pd.read_csv(datahub.GRADE_OBJECTS)
    grade_objects = df[(df['OrgUnitId'] == int(ou)) & (df['IsDeleted'] == False)]
    keys = [[i['Username'] for i in classlist], [n['DisplayName'] for n in classlist]]
    df2 = pd.DataFrame(columns=[grade_objects['GradeObjectId'].to_list(),
                                grade_objects['Name'].to_list()],
                        index=keys)
    print(df2.head())
    for user in classlist:
        grades = dwnld.get_grades_values(ou, user['Identifier'])
        for g in grades:
            df2.at[user['Username'], int(g['GradeObjectIdentifier'])] = g['DisplayedGrade']

    filename = "{}.xlsx".format(course_info['Name'])
    with pd.ExcelWriter(filename) as writer:
        df2.to_excel(writer, sheet_name='Grades')
        writer.book.add_format().set_align('center_across')
        for column in df:
            col_idx = df.columns.get_loc(column)
            writer.sheets['Grades'].set_column(col_idx, col_idx, 25)

def pdf_report():
    body = ''
    for u in classlist:
        body += "<br /><br />-----<br /><br /><b>{}</b><br />{}<br /><br />".format(u['DisplayName'], u['Username'])
        grades = dwnld.get_grades_values(ou, u['Identifier'])
        for g in grades:
            body += "{}: <b>{}</b> | ".format(g['GradeObjectName'], g['DisplayedGrade'])

    report.simple('{}.pdf'.format(course_info['Name']), course_info['Name'], body)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdf',action='store_true')
    args = parser.parse_args()
    if args.pdf:
        pdf_report()
    else:
        excel_report()
