from openpyxl import load_workbook
from archives_tools import uaLocations
from archives_tools import aspace as AS
import os

__location__ = os.path.dirname(os.path.realpath(__file__))

collectionListFile = os.path.join(__location__, "collectionList.xlsx")
collectionWorkbook = load_workbook(filename = collectionListFile, read_only=True)
collectionList = collectionWorkbook.get_sheet_by_name('collectionList')

session = AS.getSession()
repo = "2"

eadList = []
eadCount = 0
eadDir = "\\\\romeo\\Collect\\spe\\Tools\\collections"
for ead in os.listdir(eadDir):
	if ead.endswith(".xml"):
		eadCount = eadCount + 1
		eadList.append(ead.split(".xml")[0])
"""
rowIndex = 0
print "reading spreadsheet"
for row in collectionList.rows:
	rowIndex = rowIndex + 1
	if rowIndex > 1:
		if not row[0].value is None:
			if row[2].value.strip().lower() == "ead":
				eadCount = eadCount + 1
				ID = row[0].value
				eadList.append(ID)
"""
				
aspaceList = []
aspaceCount = 0				
for collection in AS.getResources(session, repo, "all"):
	aspaceCount = aspaceCount + 1
	URI = collection.uri

	if collection.id_0.startswith("nam_"):
		newID = collection.id_0.replace("nam_", "")
		collection.id_0 = newID
		aspaceList.append(newID)
		
		post = AS.postResource(session, repo, collection)
		print post
		if post != 200:
			print str(post) + "--> " + newID + ": " + URI
	else:
		aspaceList.append(collection.id_0)
					

print str(eadCount)  + " total EAD files"
print str(aspaceCount) +" in Aspace"
print str(eadCount - aspaceCount) + " missing"
missingList = []
for col in eadList:
	if not col in aspaceList:
		missingList.append(col)
print "found " + str(len(missingList)) + " missing"
print missingList