"""Returns a list of course offerings in which all users are enrolled

takes multiple X numbers as arguments
"""

import argparse

import datahub

parser = argparse.ArgumentParser()
parser.add_argument("--list", nargs="+")
args = parser.parse_args()
xlist = args.list
idlist = []

for x in xlist:
    user = datahub.get_user(x)
    idlist.append(user["UserId"])

courses = datahub.lookup_users(idlist)

if courses:
    print("----------")
    for c in courses:
        print(c["Name"])
    print("----------")
else:
    print("No common courses found")
