import json
import os

import requests

dir = os.path.dirname(__file__)
creds_json = os.path.join(dir, "records/credentials.json")

with open(creds_json) as infile:
    creds = json.load(infile)

payload = {
            "grant_type": "refresh_token",
            "refresh_token": creds["refresh_token"],
            "client_id": creds["client_id"],
            "client_secret": creds["client_secret"],
            "scope": creds["scope"]
            }

url = "https://auth.brightspace.com/core/connect/token"

headers = {'Content-Type': 'application/x-www-form-urlencoded'}

response = requests.post(url, headers=headers, data=payload)

if response.status_code == 200:
    new_creds = json.loads(response.text)
    creds.update(new_creds)
    with open(creds_json, "w") as outfile:
        json.dump(creds, outfile, indent=4)

else:
    print("Error: " + str(response.status_code))
    print(json.dumps(response.text, indent=4))
