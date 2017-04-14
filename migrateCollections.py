from openpyxl import load_workbook
from archives_tools import uaLocations
from archives_tools import aspace as AS
import os

__location__ = os.path.dirname(os.path.realpath(__file__))

collectionListFile = os.path.join(__location__, "collectionList.xlsx")
collectionWorkbook = load_workbook(filename = collectionListFile, read_only=True)
collectionList = collectionWorkbook.get_sheet_by_name('collectionList')

loginData = AS.getLogin()
#loginData = ("http://localhost:8089", "admin", "admin")
session = AS.getSession(loginData)
repo = "2"

count = 0
rowIndex = 0
collections = []
noLocation = []
for row in collectionList.rows:
	rowIndex = rowIndex + 1
	if rowIndex > 1:
		if not row[0].value is None:
			ID = row[0].value
			note = row[1].value
			collectionObject = AS.getResourceID(session, repo, ID, loginData)
			if not collectionObject is None:
				normalName = str(row[3].value).strip() + "; " + str(row[4].value).strip()
				collectionObject.finding_aid_title = normalName
				updateName = AS.postResource(session, repo, collectionObject, loginData)
				if updateName != 200:
					print ("error posting normalized name for " + ID)
			else:
				if str(row[2].value).strip() == "ead":
					#print "missing ead? " + str(row[0].value)
					pass
				else:
					collection = AS.makeResource()
					collection.id_0 = ID
					collection.ead_id = ID
					collection.finding_aid_author = "Migrated from collection-level xlsx spreadsheet."
					
					#any internal only collections
					if not row[1].value is None:
						collection.publish = False
						collection.restrictions = True
						collection.repository_processing_note = str(row[1].value)
					else:
						collection.publish = True
						collection.restrictions = False
					
					#Collection title
					collection.level = "collection"
					title = str(row[3].value).strip()
					collection.finding_aid_title = title + "; " + str(row[4].value).strip()
					collectionType = str(row[4].value)
					if collectionType.strip().lower() == "null" or collectionType.strip().lower() == "none":
						collection.title = title + " Collection"
					else:
						collection.title = title + " " + collectionType
					
					#dates
					dateField = str(row[5].value).strip()
					if dateField == "ead":
						pass
						#print "Date Error: " + ID
					elif dateField == "null" or dateField.lower() == "undated":
						collection = AS.makeDate(collection, "1600",  "2000", "Undated")
					else:
						if "-" in dateField:
							if  "ca." in dateField.lower():
								collection = AS.makeDate(collection, dateField.split("-")[0].replace("ca.", "").strip(),  dateField.split("-")[1], dateField)
							else:
								collection = AS.makeDate(collection, dateField.split("-")[0],  dateField.split("-")[1], dateField)
						else:
							if  "ca." in dateField.lower():
								collection = AS.makeDate(collection, dateField.replace("ca.", "").strip())
							else:
								collection = AS.makeDate(collection, dateField)
							
					#extent
					extentNumber = str(row[6].value).strip()
					extentType = str(row[7].value).strip()
					if extentNumber == "null" or extentType == "null":
						collection = AS.makeExtent(collection, "unknown", "uncontrolled")
					else:
						collection = AS.makeExtent(collection, extentNumber, extentType)
					
					#abstract
					abstract = str(row[8].value).strip()
					if abstract == "null":
						pass
						#print "Abstract Error: " + ID
					else:
						collection = AS.makeSingleNote(collection, "abstract", abstract)
						
					"""
					#find any matching accessions
					accessionDict = {}
					uriList = AS.findAccessions(session, repo, title, loginData)
					if len(uriList) > 0:
						for uri in uriList:
							accessionDict["ref"] = uri
					collection.related_accessions.append(accessionDict)
					"""
					
					#update record
					if rowIndex > 1:
						r = AS.postResource(session, repo, collection, loginData)
						if str(r) == "200":
							print "posted " + ID
						else:
							print "Error posting " + ID