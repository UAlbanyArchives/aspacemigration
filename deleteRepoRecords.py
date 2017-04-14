import requests
import os
import json

#for debugging
def pp(output):
	print (json.dumps(output, indent=2))
def serializeOutput(filename, output):
	__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
	f = open(os.path.join(__location__, filename + ".json"), "w")
	f.write(json.dumps(output, indent=2))
	f.close

baseURL = ""
user = ""
pw = ""

#inital request for session
r = requests.post(baseURL + "/users/" + user + "/login", data = {"password": pw})

if r.status_code == "200":
	print ("Connection Successful")

sessionID = r.json()["session"]
headers = {'X-ArchivesSpace-Session':sessionID}

repos = requests.get(baseURL + "/repositories",  headers=headers).json()
#pp(repos)
#serializeOutput("repos", repos)

#get lists of resources
allResources = requests.get(baseURL + "/repositories/2/resources?all_ids=true",  headers=headers).json()
lowNum = 99999
highNum = 0
for resourceNum in allResources:
	if resourceNum > highNum:
		highNum = resourceNum
	if resourceNum < lowNum:
		lowNum = resourceNum


for recordNum in range(lowNum, highNum + 1):
	record = str(recordNum)
	print ("deleting " + record)
	deleteAll = requests.delete(baseURL + "/repositories/2/resources/" + record,  headers=headers)
	print (deleteAll)