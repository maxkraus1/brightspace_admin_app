"""Updates the Data Hub csv tables to the Google Drive path"""

import dwnld

data_sets = [
            'Assignment Summary',
            'Content Objects',
            'Organizational Unit Descendants',
            'Organizational Units',
            'Role Details',
            'User Enrollments',
            'Users'
            ]

data_list = dwnld.get_datasets_list()

to_download = [i for i in data_list if i['Name'] in data_sets]

for item in to_download:
    path="G:/Shared drives/~ LMS Brightspace Implementation/Data Hub/Data Sets/"
    dwnld.get_dataset_csv(item['PluginId'], path)
