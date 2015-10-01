import json
import requests
import time

from requests.auth import HTTPBasicAuth

charity_list = open('charity_list.json', 'w')
json_list = []

#Quick, dirty, not future proof
for i in range(1,113):
  try:
    print("Getting page number:", i)
    list = requests.get('https://api.justgiving.com/0076b959/v1/charity/search?pagesize=100&page=' + str(i), auth=HTTPBasicAuth('ajlusardi@gmail.com', 'b1bbd510-62ea-11e5-b115'), headers={'accept':'application/json'})
    json_list.append(list.json())
    time.sleep(10)
  except:
    # If we hit an error, dump what we have
    json.dump(json_list, charity_list)

json.dump(json_list, charity_list)