"""Updates the Data Hub csv tables to the Google Drive path"""

from datetime import datetime
import io
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
            # 'Organizational Unit Descendants': None,
            'Organizational Units': 'OrgUnitId',
            'Role Details': 'RoleId',
            # 'User Enrollments': None,
            'Users': 'UserId'
            }
diffs = [d + ' Differential' for d in data_sets.keys()]
# data_list = dwnld.get_datasets_list()
exports = dwnld.get_all_bds()

to_download = [i for i in exports if i['Name'] in data_sets.keys()]
to_update = [e for e in exports if e['Name'] in diffs]
format = '%Y-%m-%dT%H:%M:%S.%fZ'

# main program
for item in to_download:
    pk = data_sets[item['Name']]
    csvfile = dwnld.get_dataset_csv(item['DownloadLink'], DATA_PATH)
    full_date = datetime.strptime(item['CreatedDate'], format)
    diff = next(d for d in to_update if d['Name'][:-13] == item['Name'])
    updates = []

    if datetime.strptime(diff['CreatedDate'], format) > full_date:
        updates.append(diff)
        for previous in diff['PreviousDataSets']:
            if datetime.strptime(previous['CreatedDate'], format) > full_date:
                updates.append(previous)
        updates.sort(key=itemgetter('CreatedDate'))  # sort by ascending date

    df = pd.read_csv(csvfile)
    df.set_index(pk, inplace=True)  # set index to primary key
    with tempfile.TemporaryDirectory() as temppath:
        for u in updates:
            update = dwnld.get_dataset_csv(previous['DownloadLink'], temppath)
            df2 = pd.read_csv(update)
            df2.set_index(pk, inplace=True)
            df3 = df.copy().reindex(index=df.index.union(df2.index))
            df3.update(df2)
            df = df3.copy()

    df.to_csv(csvfile, encoding='utf-8')
