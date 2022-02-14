"""Runner script to collect evidence for the minors

Takes a keyphrase as argument 1 and csv file as argument 2
"""

import csv
import os
import re
import sys

import datahub
import dwnld

keyphrase = sys.argv[1]
csvfile = sys.argv[2]

no_course = []
downloaded = []

with open(csvfile, newline="") as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        orgunit = row["OrgUnitId"]
        name = re.sub(r'\W+', '', row["Name"])
        coursepath = os.path.join(row["Path"], "{}_{}".format(row["Code"], name))
        try:
            if os.path.isdir(coursepath) == False:
                try:
                    os.mkdir(coursepath)
                except OSError as error:
                    print(error)
            dwnld.get_files(orgunit, keyphrase, coursepath)
        except:
            no_course.append(row)
        if len(os.listdir(coursepath)) == 0:
            os.rmdir(coursepath)
            print("No files in {}".format(row["Name"]))
        else:
            downloaded.append(os.path.basename(os.path.normpath(row["Path"])))
if no_course:
    print("Courses below were not found:")
    for row in no_course:
        print(row["Code"] + " " + row["Name"])

if downloaded:
    print("Evidence downloaded to:")
    for d in sorted(list(set(downloaded))):
        print(d)
else:
    print("No evidence downloaded")
