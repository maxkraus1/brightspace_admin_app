"""Functions to support scripts utilizing Data Hub CSV tables"""

import csv
import os

DATA_PATH = \
"G:/Shared drives/~ LMS Brightspace Implementation/Data Hub/Data Sets/"
REPORT_PATH = \
"G:/Shared drives/~ LMS Brightspace Implementation/Data Hub/Reports/"

ASSIGNMENT_SUMMARY = DATA_PATH + "AssignmentSummary.csv"
CONTENT_OBJECTS = DATA_PATH + "ContentObjects.csv"
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
        desc_reader = csv.reader(desc, delimiter=',')
        next(desc_reader)
        for row in desc_reader:
            if row[0] == str(dept):
                dept_list.append(row[1])
            if row[0] == str(sem):
                sem_list.append(row[1])
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
    """Retrieves the D2L Org Unit Id for a semester or course code"""
    with open(ORG_UNITS, newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            if row["Code"] == str(code) and row["Type"] != "Section":
                return row["OrgUnitId"]

def get_role(roleId):
    """Retrieves the role name using the role Id"""
    with open(ROLE_DETAILS,newline="",encoding="utf-8-sig") as rfile:
        roles = csv.DictReader(rfile)
        for role in roles:
            if role["RoleId"] == str(roleId):
                return role["RoleName"]

def dept_sheet(descendants):
    """Takes the results of get_descendants() and generates a list obejct
    with info of all descendants for a department
    """
    with open(ORG_UNITS, newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile, delimiter=',')
        columns = reader.fieldnames
        sheet = []
        for row in reader:
            if row['OrgUnitId'] in descendants:
                sheet.append(row)
        return [sheet, columns]

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
