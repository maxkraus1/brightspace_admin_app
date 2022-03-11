"""Updates the Data Hub csv tables to the Google Drive path"""

import json
from operator import itemgetter
import os
import tempfile

import pandas as pd

from datahub import DATA_PATH  # import path to data sets
import dwnld  # import Brightspace API methods

with open(os.path.join(os.path.dirname(__file__), "records/datasets.json")) as jsonfile:
    data_sets = json.load(jsonfile)  # load dataset names + primary keys

def composite(df, pk):
    """Sets the index of a dataframe to pk
    and handles multiple primary keys"""
    if type(pk) == list:  # check for multiple primary keys (supplied as list)
        df["PrimaryKey"] = df[pk[0]].apply(str) + "_" + df[pk[1]].apply(str)  # comine PKs into new column
        pk = "PrimaryKey"  # reset pk variable to new primary key column
    df.set_index(pk, inplace=True)  # reindex data frame to pk
    if df.index.is_unique == False:  # error handling for duplicate PK values
        print("Duplicate Values found: ", df.index.duplicated())
        df = df.loc[~df.index.duplicated(), :]  # remove duplicate values
    df.flags.allows_duplicate_labels = False  # set flag to not allow duplicate values
    return df

def main():
    diffs = [d + ' Differential' for d in data_sets.keys()]  # make list of all differential data sets
    exports = dwnld.get_all_bds()  # get all available data set downloads
    to_download = [i for i in exports if i['Name'] in data_sets.keys()]  # get list of available full data sets
    to_update = [e for e in exports if e['Name'] in diffs]  # get list of available differential data sets
    for item in to_download:
        print("Data Set: ", item['Name'])
        pk = data_sets[item['Name']]  # define primary key
        csvfile = dwnld.get_dataset_csv(item['DownloadLink'], DATA_PATH)  # get full data set
        full_date = item['CreatedDate']
        diff = next(d for d in to_update if d['Name'][:-13] == item['Name'])  # get name of differential data set
        updates = []  # initialize updates list

        if diff['CreatedDate'] > full_date:
            updates.append(diff)  # add most recent differential data set after full data set export
            for previous in diff['PreviousDataSets']:
                if previous['CreatedDate'] > full_date:
                    updates.append(previous)  # add any previous differential that are more recent than full export
            updates.sort(key=itemgetter('CreatedDate'))  # sort by ascending date

        df = composite(pd.read_csv(csvfile, dtype=str), pk)  # reindex data frame to primary key
        with tempfile.TemporaryDirectory() as temppath:
            for u in updates:
                update = dwnld.get_dataset_csv(u['DownloadLink'], temppath)  # download dataset to temppath
                df2 = composite(pd.read_csv(update, dtype=str), pk)  # reindex data frame to primary key
                # combine df + df2 index to create blank rows for inserts:
                df = df.copy().reindex(index=df.index.union(df2.index))
                # df2 rows overwrite (update) or go into blank df rows (insert):
                df.update(df2)

        df.to_csv(csvfile, encoding='utf-8')

if __name__ == "__main__":
    main()
