"""Outputs report with grades values for each courses in a department

default format is Excel with optional --pdf argument for pdf

default report is for one course with optional --dept argument for all
courses in a department
"""

import argparse
from operator import itemgetter
import os
import re
import pandas as pd

import datahub
import dwnld
import report

# add optional command line arguments
parser = argparse.ArgumentParser(add_help=True)
parser.add_argument('--pdf', action='store_true',
                    help='output PDF report instead of Excel')
parser.add_argument('--dept', action='store_true',
                    help='pull report for whole department')
parser.add_argument('--org', type=int, help='bypass inputs to call from web app')
args = parser.parse_args()

# define main function with methods for Excel and PDF formats
def main(ou, report_path):
    """produces a grades report for the ou to the report_path
    format is specified by args.pdf
    """
    classlist=sorted([u for u in dwnld.get_classlist(ou) if u['RoleId'] == 110],
                        key=itemgetter('DisplayName'))
    course_info = dwnld.get_course_info(ou)
    name_format = re.sub(r'[^\w\-_\(\) ]', '_', course_info['Name'])  # handle invalid path chars

    def excel_report():
        df = pd.read_csv(datahub.GRADE_OBJECTS)
        grade_objects = df[(df['OrgUnitId'] == int(ou)) & (df['IsDeleted'] == False)]
        keys = [[i['Username'] for i in classlist], [n['DisplayName'] for n in classlist]]
        df2 = pd.DataFrame(columns=[grade_objects['GradeObjectId'].to_list(),
                                    grade_objects['Name'].to_list()],
                            index=keys)

        for user in classlist:
            grades = dwnld.get_grades_values(ou, user['Identifier'])
            for g in grades:
                df2.at[user['Username'], int(g['GradeObjectIdentifier'])] = g['DisplayedGrade']

        filename = os.path.join(report_path, f'{name_format}.xlsx')
        with pd.ExcelWriter(filename) as writer:
            df2.to_excel(writer, sheet_name='Grades')
            writer.book.add_format().set_align('center_across')
            for column in df:
                col_idx = df.columns.get_loc(column)
                writer.sheets['Grades'].set_column(col_idx, col_idx, 25)

    def pdf_report():
        body = ''
        for u in classlist:
            body += "<br /><br />-----<br /><br /><b>{}</b>".format(u['DisplayName'])
            body += "<br />{}<br /><br />".format(u['Username'])
            grades = dwnld.get_grades_values(ou, u['Identifier'])
            for g in grades:
                body += "{}: <b>{}</b> | ".format(g['GradeObjectName'], g['DisplayedGrade'])
        filename = os.path.join(report_path, f'{name_format}.pdf')
        report.simple(filename, course_info['Name'], body)

    if args.pdf:
        pdf_report()
    else:
        excel_report()

def valid_semester_orgunits(dept_code, sem_code):
    """returns a list of OrgUnitIds for courses in the department with
    more than 0 students enrolled
    """
    filename = '{}_SemesterReport.xlsx'.format(sem_code)
    report = os.path.join(datahub.REPORT_PATH, 'Semester Course Reports', filename)
    df = pd.read_excel(report)
    df = df[(df['DeptCode'] == dept_code) & (df['StudentCount'] > 0)]
    return df['OrgUnitId'].to_list()

if __name__ == '__main__':

    if args.dept:  # check if --dept arg was provided
        dept_code = input("Enter department code: ")
        sem_code = input("Enter semester code: ")
        course_org_units = valid_semester_orgunits(dept_code, sem_code)
        report_path = os.path.join(
                                    datahub.REPORT_PATH,
                                    f'{dept_code} Nest Reports',
                                    f'{sem_code} Grades'
                                    )
        if not os.path.isdir(report_path):
            os.makedirs(report_path)
        for ou in course_org_units:
            print(f'starting report for {ou}')
            course_info = dwnld.get_course_info(ou)
            main(ou, report_path)

    else:  # default report for just one course
        if args.org:
            ou = args.org
        else:
            ou = input('enter course org unit number: ')
        report_path = datahub.REPORT_PATH
        main(ou, datahub.REPORT_PATH)

    print(f'{ou} report complete!')
    print(f'reports location: {report_path}')
