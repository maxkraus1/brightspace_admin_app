"""This module contains functions for API calls used in other scripts

The basic calls are first and the more complex ones are last

Logs are saved in dwnld_debug.log and printed to terminal
"""

import io
import json
import logging
import os
import requests
import sys
import zipfile

import auth
import report

dir = os.path.dirname(__file__)  # directory for scritps
# Logging setup to print to terminal and dwnld_debug.log
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(dir, "dwnld_debug.log")),
        logging.StreamHandler(sys.stdout)
    ]
)

# Authorization: run auth.py
token_data = json.load(open(os.path.join(dir, "credentials.json")))
HEADERS={'Authorization': 'Bearer {}'.format(token_data['access_token'])}

# Other Global Variables below
DOMAIN = 'https://lms.otis.edu/d2l/api'
LP_VERSION = '1.30'
LE_VERSION = '1.47'

def code_log(response, funct_name):
    """Helper function to log all API calls with consistent format"""
    if response.status_code < 400:
        logging.info(funct_name + " HTTP Status Code: " +
                    str(response.status_code))
    else:
        logging.error(funct_name + " HTTP Status Code: " +
                     str(response.status_code))
        response.raise_for_status()

def get_db_folders(orgUnitId, keyphrase):
    """Retrieves JSON data on all Dropbox folders in an Org Unit and
    returns a list of folderIds for matching the keyphrase
    """
    url = DOMAIN + "/le/1.47/{}/dropbox/folders/".format(orgUnitId)
    response = requests.get(url, headers=HEADERS)
    code_log(response, "GET Drobox Folders orgUnitId({})".format(orgUnitId))
    folders = json.loads(response.text)
    folderIds = []
    for item in folders:
        if keyphrase.lower() in item["Name"].lower():
            folderIds.append({"folderId": item["Id"],
                            "GradeItemId": item["GradeItemId"]})
    return folderIds

def get_submissions(orgUnitId, folderId):
    """Retrieves JSON data on all submissions for a
    given assignment Dropbox folder and returns a list of dicts
    """
    url = DOMAIN + "/le/1.47/{}/dropbox/folders/{}/submissions/".format(
                    orgUnitId, folderId)
    response = requests.get(url, headers=HEADERS)
    code_log(response, "GET Submissions orgUnitId({})".format(orgUnitId))
    submission_data = json.loads(response.text)
    return submission_data

def dwnld_stream(response, path):
    """Downloads the file stream to the path, which must include the filename"""
    with open(path, 'wb') as outfile:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                outfile.write(chunk)
    if os.path.isfile(path):
        logging.info(f"SUCCESS file: {os.path.basename(path)} downloaded")
    else:
        logging.error(f"FAILED file: {os.path.basename(path)} NOT downloaded")

def get_file(orgUnitId, folderId, submissionId, fileId, path):
    """Downloads the file to the path, which must include the filename"""
    url = DOMAIN + \
    "/le/1.47/{}/dropbox/folders/{}/submissions/{}/files/{}".format(
        orgUnitId, folderId, submissionId, fileId)
    response = requests.get(url, headers=HEADERS, stream=True)
    code_log(response, "GET File orgUnitId({})".format(orgUnitId))
    dwnld_stream(response, path)

def get_rubrics(orgUnitId, objectType, objectId):
    """Retrives a JSON arrary of Rubric blocks and returns a list of dicts"""
    url = DOMAIN + "/le/unstable/{}/rubrics".format(orgUnitId)
    params = {"objectType": objectType, "objectId": objectId}
    response = requests.get(url, headers=HEADERS, params=params)
    code_log(response, "GET Rubrics orgUnitId({})".format(orgUnitId))
    rubrics_data = json.loads(response.text)
    return rubrics_data

def get_rubric_assessment(orgUnitId, objectType, objectId, rubricId, userId):
    """Retrieves a rubric assessment repsonse and returns a dict"""
    url = DOMAIN + "/le/unstable/{}/assessment".format(orgUnitId)
    params = {
        "assessmentType": "Rubric",
        "objectType": objectType,
        "objectId": objectId,
        "rubricId": rubricId,
        "userId": userId
        }
    response = requests.get(url, headers=HEADERS, params=params)
    code_log(response, "GET rubric assessment rubricId({})".format(rubricId))
    return json.loads(response.text)

def get_attachment(orgUnitId, folderId, entityType, entityId, fileId, path):
    """retrieves an attachment from a Dropbox submission's feedback"""
    url = "{}/le/{}/{}/dropbox/folders/{}/feedback/{}/{}/attachments/{}".format(
        DOMAIN, LE_VERSION, orgUnitId, folderId, entityType, entityId, fileId)
    response = requests.get(url, headers=HEADERS)
    code_log(response, "GET attachment file Id: {}".format(fileId))
    dwnld_stream(response, path)

def get_grades_values(orgUnitId, userId):
    """Retrieves a JSON arrary of grade value blocks for one user and
    returns a list of dicts
    """
    url = DOMAIN + "/le/1.47/{}/grades/values/{}/".format(orgUnitId, userId)
    response = requests.get(url, headers=HEADERS)
    code_log(response, "GET grades values userId({})".format(userId))
    return json.loads(response.text)

def get_item_grades(orgUnitId, GradeItemId):
    """Retrieves a JSON array of all users grade values for a grade item in
    a course and returns a list of dicts
    """
    url = DOMAIN + "/le/{}/{}/grades/{}/values/".format(
        LE_VERSION, orgUnitId, GradeItemId)
    response = requests.get(url, headers=HEADERS)
    code_log(response, "GET item grades GradeItemId({})".format(GradeItemId))
    return json.loads(response.text)

def get_datasets_list():
    """Retrieves the list of Brightspace Data Sets and
    returns a list of dicts
    """
    url = DOMAIN + "/lp/{}/dataExport/bds/list".format(LP_VERSION)
    response = requests.get(url, headers=HEADERS)
    code_log(response, "GET data sets list")
    return json.loads(response.text)

def get_all_bds():
    """Retrieves the paginated list of all available BDS exports and returns a
    list of dicts"""
    url = DOMAIN + "/lp/{}/dataExport/bds".format(LP_VERSION)
    exports = []
    page = 1
    while url != None:
        response = requests.get(url, headers=HEADERS)
        code_log(response, "GET all BDS exports page {}".format(page))
        data = json.loads(response.text)
        exports.extend(data["BrightspaceDataSets"])
        url = data["NextPageUrl"]
        page += 1
    return exports

def get_dataset_csv(url, path):
    """Downloads the data set csv file to the path"""
    response = requests.get(url, headers=HEADERS, stream=True)
    code_log(response, "GET data set csv")
    with zipfile.ZipFile(io.BytesIO(response.content), 'r') as zip_ref:
        contents = zip_ref.namelist()
        assert len(contents) == 1
        zip_ref.extractall(path)
        return os.path.join(path, contents[0])

def get_toc(orgUnitId):
    """Retrieves the Table of Contents for the course and
    returns a list of dicts
    """
    url = DOMAIN + "/le/1.47/{}/content/toc".format(orgUnitId)
    params = {'ignoreModuleDateRestrictions': True}
    response = requests.get(url, headers=HEADERS, params=params)
    code_log(response, 'GET {} Table of Contents'.format(orgUnitId))
    return json.loads(response.text)

def course_copy(destId, sourceId, components=None):
    """Issues a copy course request for the list of components
    (if blank, it will copy all components)
    """
    url = DOMAIN + "/le/1.47/import/{}/copy/".format(destId)
    body = {"SourceOrgUnitId": sourceId,
            "Components": components,
            "CallbackUrl": ""}
    response = requests.post(url, headers=HEADERS, json=body)
    code_log(response, "POST Course copy {} to {} {}".format(sourceId,
                                                            destId,
                                                            response.text))

def get_copy_logs(params=None):
    """retrieves course copy logs for the selected parameters"""
    url = DOMAIN + "/le/unstable/ccb/logs"
    response = requests.get(url, headers=HEADERS, params=params)
    return response.status_code

def get_children(orgUnitId, ouTypeId=None):
    """Returns a list of dicts of all child org units.
    Optional to specify Org Unit Type of children.
    """
    url = DOMAIN + "/lp/{}/orgstructure/{}/children/paged/".format(LP_VERSION,
                                                            orgUnitId)
    flag = True
    params = {}
    children = []
    if ouTypeId:
        params['ouTypeId'] = ouTypeId
        print("Org Unit Type Id: {}".format(ouTypeId))
    while flag == True:
        response = requests.get(url, headers=HEADERS, params=params)
        code_log(response, "GET children of {} (paged)".format(orgUnitId))
        page = json.loads(response.text)
        params['bookmark'] = page['PagingInfo']['Bookmark']
        children.extend(page['Items'])
        if page['PagingInfo']['HasMoreItems'] == False:
            flag = False
    return children

def get_classlist(orgUnitId):
    """Returns a list of dicts for users enrolled in the org unit"""
    url = DOMAIN + "/le/{}/{}/classlist/".format(LE_VERSION, orgUnitId)
    response = requests.get(url, headers=HEADERS)
    code_log(response, "GET class list for org unit {}".format(orgUnitId))
    return json.loads(response.text)

def get_course_info(orgUnitId):
    """Returns basic info for a course offering"""
    url = DOMAIN + "/lp/{}/courses/{}".format(LP_VERSION, orgUnitId)
    response = requests.get(url, headers=HEADERS)
    code_log(response, "GET course offering info org unit".format(orgUnitId))
    return json.loads(response.text)

def put_course_info(orgUnitId, json_data):
    """Updates the course info for a particular org unit"""
    url = DOMAIN + "/lp/{}/courses/{}".format(LP_VERSION, orgUnitId)
    response = requests.put(url, headers=HEADERS, json=json_data)
    code_log(response, "PUT course offering info org unit {}".format(orgUnitId))

def enroll(orgUnitId, userId, roleId, isCascading=False):
    """enrolls a user in the org unit"""
    url = DOMAIN + "/lp/{}/enrollments/".format(LP_VERSION)
    data = {"OrgUnitId": orgUnitId,"UserId": userId,"RoleId": roleId,"IsCascading": isCascading}
    response = requests.post(url, headers=HEADERS, json=data)
    code_log(response, "POST enroll user {} to org unit {}".format(userId, orgUnitId))

# complex functions below here
def get_files(orgUnitId, keyphrase, path):
    """Creates a Rubric Assessment file and downloads the submitted file."""
    folderIds = get_db_folders(orgUnitId, keyphrase)
    if folderIds == []:
        return "No Dropbox folders match the keyphrase!"
    for folder in folderIds:
        submission_data = get_submissions(orgUnitId, folderId)
        grades_data = None
        if folder["GradeItemId"]:
            grades_data = get_item_grades(orgUnitId, folder["GradeItemId"])
        for item in submission_data:
            name = item["Entity"]["DisplayName"]
            entityId = item["Entity"]["EntityId"]
            entityType = item["Entity"]["EntityType"]

            flag = False
            if grades_data:
                for g in grades_data["Objects"]:
                    if g["User"]["Identifier"]==str(item["Entity"]["EntityId"]):
                        if g["GradeValue"]:
                            flag = True
                            grade = g["GradeValue"]["DisplayedGrade"]
                            name += f"__{grade}_"
            elif flag == False:
                name += "__[No Grade]_"

            if item["Feedback"]:
                file_list = item["Feedback"]["Files"]
                for file in file_list:
                    print("found!!!!")
                    fileId = file["FileId"]
                    filename = file["FileName"]
                    afilename = "{}_AttachmentFeedback_{}".format(name,
                                                                filename)
                    attach_path = os.path.join(path, afilename)
                    get_attachment(orgUnitId, folder["folderId"], entityType,
                                entityId, fileId, attach_path)
                if item["Feedback"]["Feedback"]:
                    feedback = item["Feedback"]["Feedback"]["Html"]
                    fbfile = os.path.join(path, f"{name}_OverallFeedback.pdf")
                    report.simple(fbfile, "Overall Feedback", feedback)
                if item["Feedback"]["RubricAssessments"]:
                    assessments = item["Feedback"]["RubricAssessments"]
                    rubrics = get_rubrics(
                        orgUnitId, "Dropbox", folder["folderId"])
                    rfile = os.path.join(path, f"{name}_RubricAssessments.pdf")
                    report.rubric_assessments(rfile, assessments, rubrics)
                    if os.path.isfile(rfile):
                        logging.info(
                            f"SUCCESS {os.path.basename(rfile)} created")
                    else:
                        logging.error(
                            f"FAILED {os.path.basename(rfile)} NOT created")

            for submission in item["Submissions"]:
                submissionId = submission["Id"]
                for file in submission["Files"]:
                    filename = file["FileName"]
                    fileId = file["FileId"]
                    filepath = os.path.join(path, f"{name}_{filename}")
                    get_file(orgUnitId,
                            folder["folderId"],
                            submissionId,
                            fileId,
                            filepath)
