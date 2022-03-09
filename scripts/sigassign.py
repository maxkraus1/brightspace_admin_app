"""Runner script for downloading Signature Assignments

Takes a path for the semester folder as argument 1

Takes a CSV file (Course Title and OrgUnitId must both be columns) of
courses to download assignments from as argument 2

For each course, creates a folder inside the semester path and
performs dwnld.get_files()
"""

import csv
import os
import sys

import dwnld

keyphrase = "Signature Assignment"  # can replace with another term, like "Final Project"
path = sys.argv[1]
to_download = sys.argv[2]

with open(to_download, newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for line in reader:
        orgUnitId = line["OrgUnitId"]
        orgname = line["Course Title"]
        coursepath = os.path.join(path, orgname)
        try:
            os.mkdirs(coursepath)
            dwnld.get_files(orgUnitId, keyphrase, coursepath)
        except:
            if os.isdir(coursepath):
                print(f"{coursepath} already exists")
            else:
                print(f"Org Unit {orgUnitId} NOT DOWNLOADED")
