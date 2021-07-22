"""Functions to support scripts utilizing Data Hub CSV tables"""

from collections import Counter
import csv
import os
import re

import pandas as pd

DATA_PATH = \
"G:/Shared drives/~ LMS Brightspace Implementation/Data Hub/Data Sets/"
REPORT_PATH = \
"G:/Shared drives/~ LMS Brightspace Implementation/Data Hub/Reports/"

ASSIGNMENT_SUMMARY = DATA_PATH + "AssignmentSummary.csv"
CONTENT_OBJECTS = DATA_PATH + "ContentObjects.csv"
GRADE_OBJECTS = DATA_PATH + "GradeObjects.csv"
DESCENDANTS = DATA_PATH + "OrganizationalUnitDescendants.csv"
ORG_UNITS = DATA_PATH + "OrganizationalUnits.csv"
ROLE_DETAILS = DATA_PATH + "RoleDetails.csv"
USER_ENROLLMENTS = DATA_PATH + "UserEnrollments.csv"
USERS = DATA_PATH + "Users.csv"

def get_descendants(dept, sem):
    """Takes a department and semester OrgUnitId and
    returns the descendent Org Unit IDs
    """
    desc_list = []
    dept_list = []
    sem_list = []
    with open(DESCENDANTS, newline="", encoding="utf-8-sig") as desc:
        desc_reader = csv.DictReader(desc, delimiter=',')
        for row in desc_reader:
            if row["OrgUnitId"] == str(dept):
                dept_list.append(row["DescendantOrgUnitId"])
            if row["OrgUnitId"] == str(sem):
                sem_list.append(row["DescendantOrgUnitId"])
        for id in dept_list:
            if id in sem_list:
                desc_list.append(id)
        return desc_list

def get_code(orgUnitId):
    """Takes a OrgUnitId and returns its code"""
    with open(ORG_UNITS, newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            if row["OrgUnitId"] == str(orgUnitId):
                 return row["Code"]

def get_user(id):
    """Retrives info on a user from their X number"""
    with open(USERS, newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        try:
            field = "OrgDefinedId" if id[0] == "X" else "UserId"
        except:
            field = "UserId"
        for row in reader:
            if row[field] == str(id):
                return row

def get_enrollments(orgUnitId):
    """retrives users enrolled in an org unit"""
    with open(USER_ENROLLMENTS, newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        enrollments = []
        for row in reader:
            if row["OrgUnitId"] == str(orgUnitId):
                enrollments.append(row)
        return enrollments

def get_orgunit(code):
    """Retrieves the D2L Org Unit Id for a semester, department, or course"""
    with open(ORG_UNITS, newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        orgunit = None
        for row in reader:
            if str(row["Code"]) == str(code) and row["Type"] != "Section":
                if orgunit == None:
                    orgunit = row["OrgUnitId"]
                else:
                    print("Multiple Org Unit matches for {}".format(code))
                    orgunit = input("Please enter Org Unit Id number: ")
                    return orgunit
        if orgunit != None:
            return orgunit
        else:
            raise ValueError("No org units found for {}".format(code))

def get_role(roleId):
    """Retrieves the role name using the role Id"""
    with open(ROLE_DETAILS,newline="",encoding="utf-8-sig") as rfile:
        roles = csv.DictReader(rfile)
        for role in roles:
            if role["RoleId"] == str(roleId):
                return role["RoleName"]

def dept_index():
    """returns a dataframe of OrgUnitId|DeptCode"""
    ou = pd.read_csv(ORG_UNITS, dtype="string")
    ou = ou[ou.Type == "Department"]
    ou.rename(columns={"Code": "DeptCode"}, inplace=True)
    desc = pd.read_csv(DESCENDANTS, dtype="string")
    df = ou.set_index("OrgUnitId").join(desc.set_index("OrgUnitId"))
    df.set_index("DescendantOrgUnitId", inplace=True)
    return df[["DeptCode"]].copy()

def instructor_index():
    """returns a dataframe of OrgUnitId|XNumber|Email"""
    users = pd.read_csv(USERS, dtype="string")
    df1 = pd.read_csv(USER_ENROLLMENTS, dtype="string")
    df1 = df1[df1.RoleName == "Faculty / Instructor"]
    df1 = df1.filter(items=["OrgUnitId", "UserId"])
    df2 = df1.merge(users, how="left", on="UserId")
    df2 = df2.filter(items=['OrgUnitId', 'UserName', 'ExternalEmail'])
    df3 = df2.astype(str).groupby(["OrgUnitId"], as_index=False).agg(
                            {"UserName": ",".join, "ExternalEmail": ",".join})
    return df3.rename(columns={
                            "UserName": "InstructorXnumber",
                            "ExternalEmail": "InstructorEmail"})

def stud_enroll_index():
    """returns a series of OrgUnitId: StudentCount"""
    df = pd.read_csv(USER_ENROLLMENTS, dtype="string")
    df = df[df.RoleName == "Student / Learner"]
    counts = df.value_counts("OrgUnitId", sort=False)
    return counts.rename("StudentCount")

def content_obj_counts():
    """returns a series of OrgUnitId: ContentObjCount"""
    df = pd.read_csv(CONTENT_OBJECTS, dtype="string")
    counts = df.value_counts("OrgUnitId", sort=False)
    return counts.rename("ContentObjCount")

def get_semester_courses(orgUnitId):
    """takes the Otis semester code and returns a list of dicts for each
    course offering in the semester
    """
    ou_list = []
    with open(DESCENDANTS, newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            if row["OrgUnitId"] == str(orgUnitId):
                ou_list.append(row["DescendantOrgUnitId"])
    course_list = []
    with open(ORG_UNITS, newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            if row["OrgUnitId"] in ou_list and row["Type"] == "Course Offering":
                course_list.append(row)
    return course_list

def get_grade_objects(orgUnitId):
    """returns a dict for each grade object in a list"""
    with open(GRADE_OBJECTS, newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        return [r for r in reader if r["OrgUnitId"] == orgUnitId]

def cross_listed(orgUnitId):
    """Takes the semester Org Unit Idand produces a csv report on all
    cross-listed courses in the semester
    """
    all_courses = get_semester_courses(orgUnitId)
    pattern = r"\(([A-Z]{4}.+)\)"
    cross_listed = []
    for c in all_courses:
        result = re.search(pattern, c["Name"])
        if len(result.group(1)) > 11:
            cross_listed.append(c)
    return pd.DataFrame(cross_listed)


def dept_sheet(descendants):
    """Takes the results of get_descendants() and generates a list obejct
    with info of all course offerings for a department
    """
    with open(ORG_UNITS, newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile, delimiter=',')
        columns = reader.fieldnames
        sheet = []
        for row in reader:
            if row['OrgUnitId'] in descendants:
                if row['Type'] == "Course Offering":
                    sheet.append(row)
        return [sheet, columns]

def lookup_users(idlist):
    """returns the course offerings in which all users in idlist are enrolled"""
    courses = []
    with open(USER_ENROLLMENTS, newline="", encoding="utf-8-sig") as file1:
        reader1 = csv.DictReader(file1)
        orgs = [e["OrgUnitId"] for e in reader1 if e["UserId"] in idlist]
        org_count = Counter(orgs)
        with open(ORG_UNITS, newline="", encoding="utf-8-sig") as file2:
            reader2 = csv.DictReader(file2)
            for row in reader2:
                ouid = row["OrgUnitId"]
                if ouid in orgs and org_count[ouid] == len(idlist):
                    if row["Type"] == "Course Offering":
                        courses.append(row)
    return courses

def signature_assignments(sem):
    """ Takes a semester OrgUnitId and writes a CSV file of assignments in the
    semester with Signature Assignments to DATA_PATH
    """
    libs = 6705
    all_courses = get_descendants(libs, sem)
    with open(ASSIGNMENT_SUMMARY, newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile, delimiter=',')
        headers = reader.fieldnames
        sig_list = []
        for row in reader:
            if row['OrgUnitId'] in all_courses and \
                'Signature Assignment' in row['Name']:
                sig_list.append(row)
        codes = get_code(libs, sem)
        report = '{}Signature Assignments_{}.csv'.format(DATA_PATH, codes[1])
        with open(report, 'w', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=headers)
            writer.writeheader()
            for row in sig_list:
                writer.writerow(row)
    if os.path.isfile(report):
        print("{} created".format(os.path.basename(report)))
    else:
        raise ValueError('No Report Created')

def add_org_column(csvfile):
    """takes a csvfile and adds an org unit column"""
    with open(csvfile, newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        fields = reader.fieldnames
        rows = [r for r in reader]
    fields.append("OrgUnitId")
    split = os.path.split(csvfile)
    newfile = os.path.join(split[0], "EDIT_" + os.path.basename(csvfile))
    with open(newfile, "w", newline="", encoding="utf-8-sig") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            try:
                row["OrgUnitId"] = get_orgunit(str(row["Code"]))
            except ValueError as error:
                print(error)
                row["OrgUnitId"] = None
            writer.writerow(row)
