"""Returns a CSV report of users enrolled in a department and/or semester"""

import csv
from datetime import datetime
from operator import itemgetter
import os

import datahub

semester = input("Enter Otis semester code: ")
department = input("Enter Otis department code (for all departments enter 0): ")
role_input = input("Enter 1 for students or 2 for faculty: ")
role = "110" if role_input == "1" else "109"
role_name = "Students" if role == "110" else "Faculty"

sem = datahub.get_orgunit(semester)
dept = 6606 if department == '0' else datahub.get_orgunit(department)
descendants = datahub.get_descendants(sem, dept)

print("Finding enrollments...")
enrollments = []
for d in descendants:
    enrollments.extend(datahub.get_enrollments(d))

print("Fetching user info...")
ids = []
users = []
for e in enrollments:
    if e["RoleId"] == role and e["UserId"] not in ids:
        users.append(datahub.get_user(e["UserId"]))
    ids.append(e["UserId"])
users.sort(key=itemgetter("LastName"))

timestamp = datetime.now().strftime("%Y-%m-%d")
filename=os.path.join(datahub.REPORT_PATH, "{}_{}_{}_{}.csv".format(
                                    semester, department, role_name, timestamp))

with open(filename, "w", newline="") as csvfile:
    fieldnames = ["Name", "Email"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for u in users:
        writer.writerow({"Name": "{} {}".format(u["FirstName"],u["LastName"]),
                        "Email": u["ExternalEmail"]})
print(f"File now available: {filename}")
