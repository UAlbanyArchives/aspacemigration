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

rowIndex = 0
collections = []
noLocation = []
for row in collectionList.rows:
	rowIndex = rowIndex + 1
	if rowIndex > 1:
		ID = row[0].value
		print (ID)
		if not row[15].value is None:
			locationCode = row[15].value
			
			for place in str(locationCode).split(";"):
				coordinateList = uaLocations.location2ASpace(place.strip())
				
				if coordinateList[1] is False:
					#single location
					locTitle = coordinateList[0]["Title"]
					if len(locTitle) < 1:
						for x in str(locationCode).split(";"):
							print x.strip()
					locationURI = AS.findLocation(session, locTitle, loginData)
					
					#collectionObject = AS.getResourceID(session, repo, ID, loginData)
					#tree = AS.getTree(session collectionObject, loginData)
					
					#boxObject = AS.addToLocation(boxObject, locationURI, coordinateList[0]["Note"], loginData)
					
				else:
					#multiple locations
					locList = []
					for location in coordinateList[0]:
						locTitle = location["Title"]
						locNote = location["Note"]
						locationURI = AS.findLocation(session, locTitle, loginData)
						#locList.append([locationURI, locNote])