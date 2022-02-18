"""Retrieves the Roster for each class and outputs an Excel file

Choose to supply department/semester codes (--dept and --sem) OR
a csv file (--csv) to select the courses to be included in the report
"""

import argparse
import csv
import re
import os

import pandas as pd

import datahub
import dwnld

role_details = datahub.ROLE_DETAILS

# add arguments for differnt course selecting options
parser = argparse.ArgumentParser()
parser.add_argument('--sem', help='semester code')
parser.add_argument('--dept', help='department code')
parser.add_argument('--csv', help='csv file with OrgUnitId, Name and Code as columns')
args = parser.parse_args()

# set variables depending on args
if args.sem and args.dept:
    sem, dept = args.sem, args.dept
    sem_ou = datahub.get_orgunit(semester)
    dept_ou = datahub.get_orgunit(department)
    courses = datahub.dept_sheet(datahub.get_descendants(dept_ou, sem_ou))[0]
    filename = os.path.join(datahub.REPORT_PATH,"{}_{}_Rosters".format(sem,dept))
elif args.csv:
    df = pd.read_csv(args.csv, dtype=str)
    courses = df.to_dict('records')
    filename = os.path.join(datahub.REPORT_PATH,"{}_Rosters".format(os.path.basename(args.csv)[:-4]))
else:  # raise error if no arguments are supplied
    raise argparse.ArgumentError('Either --sem and --dept or --csv must be provided')

writer = pd.ExcelWriter(filename + ".xlsx")
workbook = writer.book
title_format = workbook.add_format({"bold": True,
                                "font_color": "#4D9C34",
                                "font_size": 16})
# build report
for row in courses:
    roster = dwnld.get_classlist(row["OrgUnitId"])
    for user in roster:
        user["Role"] = datahub.get_role(user["RoleId"])

    result = re.search(r"\((.+)\)", row["Name"])  # get course code from Name
    code = result.group(1)
    columns = ["FirstName", "LastName", "Username", "Email", "Role"]
    df = pd.DataFrame(roster, columns=columns)
    df.sort_values(['LastName'], inplace=True)  # Sort by Last Name
    df.to_excel(writer, sheet_name=code, startrow=2, index=False)

    # format columns
    worksheet = writer.sheets[code]
    worksheet.write(0,0, row['Name'], title_format)
    worksheet.write(1,0, "CRN: {}".format(row["Code"][:5]), title_format)
    worksheet.set_column('A:A', 15)
    worksheet.set_column('B:B', 15)
    worksheet.set_column('C:C', 12)
    worksheet.set_column('D:D', 25)
    worksheet.set_column('E:E', 20)

writer.save()
