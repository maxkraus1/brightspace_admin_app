"""Functions to support scripts utilizing Data Hub CSV tables"""

from collections import Counter
import csv
import os
import re

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

def get_user(xnumber):
    """Retrives info on a user from their X number"""
    with open(USERS, newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            if row["OrgDefinedId"] == xnumber:
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

def get_semester_courses(orgUnitId):
    """takes the Otis semester code and returns a list of dicts for each
    course offering in the semester
    """
    ou_list = []
    with open(DESCENDANTS, newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            if row["OrgUnitId"] == orgUnitId:
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
    semestercode = get_code(orgUnitId)
    pattern = r"[A-Z]{2}" + str(semestercode)
    cross_listed = [c for c in all_courses if re.match(pattern, c["Code"])]
    filename = os.path.join(REPORT_PATH,
        "Semester Course Reports/{}_CrossListed.csv".format(semestercode))
    with open(filename, "w", newline="") as outfile:
        fieldnames = all_courses[0].keys()
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cross_listed)

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
