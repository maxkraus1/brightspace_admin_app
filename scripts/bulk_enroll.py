"""Enrolls users in a orgUnit specified in a CSV file

CSV file should have 'OrgUnitId', 'Xnumber', and 'RoleId' columns
"""
import sys

import pandas as pd

import datahub
import dwnld

df = pd.read_csv(sys.argv[1])
for i, r in df.iterrows():
    user = datahub.get_user(r['Xnumber'])
    dwnld.enroll(r['OrgUnitId'],user['UserId'],r['RoleId'])
