"""Updates data for course offerings in a csv file

Takes csv file as the first argument and a comma separated string of
key=value pairs as the second argument (i.e. Name=Course1,Code=12345)
"""

import argparse
import os
import pandas as pd

import dwnld

parser = argparse.ArgumentParser()
parser.add_argument("csv", help="path to csv file with OrgUnitId column")
class StoreDictKeyPair(argparse.Action):
     def __call__(self, parser, namespace, values, option_string=None):
         my_dict = {}
         for kv in values.split(","):
             k,v = kv.split("=")
             my_dict[k] = v
         setattr(namespace, self.dest, my_dict)

parser.add_argument("key_pairs", action=StoreDictKeyPair, metavar="KEY1=VAL1,KEY2=VAL2...")
args = parser.parse_args()

df = pd.read_csv(args.csv)
to_update = df['OrgUnitId'].to_list()
update_data = args.key_pairs

for id in to_update:
    data = dwnld.get_course_info(id)
    new_data = {
                "Name": data["Name"],
                "Code": data["Code"],
                "StartDate": data["StartDate"],
                "EndDate": data["EndDate"],
                "IsActive": data["IsActive"],
                "Description": {
                                "Content": data["Description"]["Text"],
                                "Type": "Text"
                                },
                "CanSelfRegister": data["CanSelfRegister"]
                }
    for k in update_data.keys():
        new_data[k] = update_data[k]
    dwnld.put_course_info(id, new_data)
