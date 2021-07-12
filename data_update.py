"""Updates the Data Hub csv tables to the Google Drive path"""

import json
from operator import itemgetter
import os
import tempfile

import pandas as pd

from datahub import DATA_PATH
import dwnld

with open(os.path.join(os.path.dirname(__file__), "datasets.json")) as jsonfile:
    data_sets = json.load(jsonfile)

def composite(df, pk):
    """Sets the index of a dataframe to pk
    and handles multiple primary keys"""
    if type(pk) == list:
        df["PrimaryKey"] = df[pk[0]].apply(str) + "_" + df[pk[1]].apply(str)
        pk = "PrimaryKey"
    df.set_index(pk, inplace=True)
    return df

def main():
    diffs = [d + ' Differential' for d in data_sets.keys()]
    exports = dwnld.get_all_bds()
    to_download = [i for i in exports if i['Name'] in data_sets.keys()]
    to_update = [e for e in exports if e['Name'] in diffs]
    for item in to_download:
        pk = data_sets[item['Name']]  # define primary key
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

        df = composite(pd.read_csv(csvfile, dtype=str), pk)
        with tempfile.TemporaryDirectory() as temppath:
            for u in updates:
                update = dwnld.get_dataset_csv(u['DownloadLink'], temppath)
                df2 = composite(pd.read_csv(update, dtype=str), pk)
                # combine df + df2 index to create blank rows for inserts:
                df = df.copy().reindex(index=df.index.union(df2.index))
                # df2 rows overwrite (update) or go into blank df rows (insert):
                df.update(df2)

        df.to_csv(csvfile, encoding='utf-8')

if __name__ == "__main__":
    main()
