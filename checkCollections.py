from openpyxl import load_workbook
from archives_tools import uaLocations
from archives_tools import aspace as AS
import os

__location__ = os.path.dirname(os.path.realpath(__file__))

collectionListFile = os.path.join(__location__, "collectionList.xlsx")
collectionWorkbook = load_workbook(filename = collectionListFile, read_only=True)
collectionList = collectionWorkbook.get_sheet_by_name('collectionList')

loginData = AS.getLogin()
session = AS.getSession(loginData)
repo = "2"

count = 0
rowIndex = 0
spreadCollections = []
for row in collectionList.rows:
	rowIndex = rowIndex + 1
	if rowIndex > 1:
		if not row[0].value is None:
			ID = row[0].value
			note = row[1].value
			spreadCollections.append(ID)

			collectionObject = AS.getResourceID(session, repo, ID, loginData)
			if collectionObject is None:
				count = count + 1
				#print ID + " not present, note issue"
				print row[2].value
				if row[2].value != "null":
					print ID + "<----------------------------"
			else:
				collectionID =  collectionObject.id_0

				
print str(count) + " missing in ASpace"

aspaceList = []
aspaceCount = 0				
for collection in AS.getResources(session, repo, "all"):
	aspaceCount = aspaceCount + 1
	aspaceList.append(collection.id_0)
	
print str(aspaceCount) + " records in ASpace"
print str(len(spreadCollections)) + " records in spreadsheet"
oddList = []
for col in aspaceList:
	if not col in spreadCollections:
		oddList.append(col)
		
print oddList