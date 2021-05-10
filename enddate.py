"""Updates the end date for course offerings in a csv file

Takes Otis semester code as command line argument 1 and the end date as
command line argument 2
"""

import csv
import os
import sys

import datahub
import dwnld

csvfile = os.path.join(datahub.REPORT_PATH,
            "Semester Course Reports/{}_CrossListed.csv".format(sys.argv[1]))
enddate = str(sys.argv[2])

with open(csvfile, newline="", encoding="utf-8-sig") as infile:
    reader = csv.DictReader(infile)
    to_update = []
    for line in reader:
        to_update.append(line["OrgUnitId"])

for id in to_update:
    data = dwnld.get_course_info(id)
    new_data = {
                "Name": data["Name"],
                "Code": data["Code"],
                "StartDate": data["StartDate"],
                "EndDate": enddate,
                "IsActive": data["IsActive"],
                "Description": {
                                "Content": data["Description"]["Text"],
                                "Type": "Text"
                                },
                "CanSelfRegister": data["CanSelfRegister"]
                }
    dwnld.put_course_info(id, new_data)
