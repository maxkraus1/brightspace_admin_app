"""Updates the Data Hub csv tables to the Google Drive path"""

from operator import itemgetter
import tempfile

import pandas as pd

from datahub import DATA_PATH
import dwnld

data_sets = {  # Name: Primary Key
            'Assignment Summary': 'DropboxId',
            'Calendar Events': 'ScheduleId',
            'Content Objects': 'ContentObjectId',
            'Grade Objects': 'GradeObjectId',
            'Organizational Unit Descendants': ['OrgUnitId', 'DescendantOrgUnitId'],
            'Organizational Units': 'OrgUnitId',
            'Role Details': 'RoleId',
            'User Enrollments': ['OrgUnitId', 'UserId'],
            'Users': 'UserId'
            }
diffs = [d + ' Differential' for d in data_sets.keys()]
# data_list = dwnld.get_datasets_list()
exports = dwnld.get_all_bds()

to_download = [i for i in exports if i['Name'] in data_sets.keys()]
to_update = [e for e in exports if e['Name'] in diffs]

def composite(df, pk):
    """creates a primary key from 2 columns in a dataframe"""
    if type(pk) == list:
        df["PrimaryKey"] = df[pk[0]].apply(str) + "_" + df[pk[1]].apply(str)
    return df

# main program
for item in to_download:
    pk = data_sets[item['Name']]
    csvfile = dwnld.get_dataset_csv(item['DownloadLink'], DATA_PATH)
    full_date = item['CreatedDate']
    diff = next(d for d in to_update if d['Name'][:-13] == item['Name'])
    updates = []

    if diff['CreatedDate'] > full_date:
        updates.append(diff)
        for previous in diff['PreviousDataSets']:
            if previous['CreatedDate'] > full_date:
                updates.append(previous)
        updates.sort(key=itemgetter('CreatedDate'))  # sort by ascending date

    df = composite(pd.read_csv(csvfile), pk)
    if type(pk) == list:
        df.set_index("PrimaryKey", inplace=True)
    else:
        df.set_index(pk, inplace=True)
    with tempfile.TemporaryDirectory() as temppath:
        for u in updates:
            update = dwnld.get_dataset_csv(u['DownloadLink'], temppath)
            df2 = composite(pd.read_csv(update), pk)
            if type(pk) == list:
                df2.set_index("PrimaryKey", inplace=True)
            else:
                df2.set_index(pk, inplace=True)
            df = df.copy().reindex(index=df.index.union(df2.index))
            df.update(df2)

    df.to_csv(csvfile, encoding='utf-8')
