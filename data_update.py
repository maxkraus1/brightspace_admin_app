"""Updates the Data Hub csv tables to the Google Drive path"""

import csv
from datetime import datetime
import io
import os
import tempfile

from datahub import DATA_PATH
import dwnld

data_sets = [
            'Assignment Summary',
            'Calendar Events',
            'Content Objects',
            'Organizational Unit Descendants',
            'Organizational Units',
            'Role Details',
            'User Enrollments',
            'Users'
            ]
diffs = [d + ' Differential' for d in data_sets]
# data_list = dwnld.get_datasets_list()
exports = dwnld.get_all_bds()

to_download = [i for i in exports if i['Name'] in data_sets]
to_update = [e for e in exports if e['Name'] in diffs]

# helper function
def extend_list(update, updates):
    with open(update, newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        next(reader)
        for row in reader:
            updates.append(row)

# main program
for item in to_download:
    dwnld.get_dataset_csv(item['DownloadLink'], DATA_PATH)
    filename = item['Name'].replace(' ','')
    csvfile = os.path.join(DATA_PATH, '{}.csv'.format(filename))
    format = '%Y-%m-%dT%H:%M:%S.%fZ'
    full_date = datetime.strptime(item['CreatedDate'], format)
    updates = []
    diff = next(d for d in to_update if d['Name'][:-13] == item['Name'])
    if datetime.strptime(diff['CreatedDate'], format) > full_date:
        with tempfile.TemporaryDirectory() as temppath:
            update = dwnld.get_dataset_csv(diff['DownloadLink'], temppath)
            extend_list(update, updates)
            for previous in diff['PreviousDataSets']:
                if datetime.strptime(previous['CreatedDate'], format) > full_date:
                    update = dwnld.get_dataset_csv(previous['DownloadLink'], temppath)
                    extend_list(update, updates)

    with open(csvfile, 'a', newline='', encoding='utf-8-sig') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(updates)
