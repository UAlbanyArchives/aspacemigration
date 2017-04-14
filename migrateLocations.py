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

rowIndex = 0
collections = []
noLocation = []
for row in collectionList.rows:
	rowIndex = rowIndex + 1
	if rowIndex > 49:
		print ("***********************************************************************************************************")
		ID = row[0].value
		print (str(rowIndex) + ". " + ID)
		if not row[15].value is None:
			locationCode = row[15].value
			if not ";" in str(locationCode):
				#single location
				coordinateList = []
				coordinates = uaLocations.location2ASpace(str(locationCode).strip())
				if coordinates[1] is True:
					for coordSet in coordinates[0]:
						coordinateList.append(coordSet)
				else:
					coordinateList.append(coordinates[0])
				
				collectionObject = AS.getResourceID(session, repo, ID, loginData)
				#take this out before production migration
				if collectionObject is None:
					pass
				else:
					hasChildren = False
					tree = AS.getTree(session, collectionObject, loginData)
					for child in tree.children:
						if not "website" in child.title.lower() and not "web archives" in child.title.lower():
							hasChildren = True
					if hasChildren == False:
						boxObject = AS.makeContainer(session, repo, "Collection", "X", loginData)
						for location in coordinateList:
							locationURI = AS.findLocation(session, location["Title"], loginData)
							locFound = False
							if len(boxObject.container_locations) > 0:
								for listedLoc in boxObject.container_locations:
									if listedLoc["ref"] == locationURI:
										locFound = True
							if locFound == False:
								boxUpdates = True
								locationObject = AS.getLocation(session, locationURI, loginData)
								if len(coordinateList) > 1:
									locationObject.temporary = "collection_level"
									post0 = AS.postLocation(session, locationObject, loginData)
									if post0 != 200:
										print ("location:" + str(post0))
									boxObject = AS.addToLocation(boxObject, locationURI, location["Note"], "previous", "2999-01-01")
								else:
									boxObject = AS.addToLocation(boxObject, locationURI)
						post1 = AS.postContainer(session, repo, boxObject, loginData)
						if post1 != 200:
							print (post1)
						collectionObject = AS.addToContainer(session, collectionObject, boxObject.uri, None, None, loginData)
						post2 = AS.postResource(session, repo, collectionObject, loginData)			
						if post2 != 200:
							print (post2)
					else:
						uriList = []
						def findBoxes(tree, uriList):
							for child in tree.children:			
								if len(child.containers) < 1:
									findBoxes(child, uriList)
								else:
									aoObject = AS.getArchObj(session, child.record_uri, loginData)
									for box in aoObject.instances:
										if "sub_container" in box.keys():
											boxURI = box.sub_container.top_container.ref
											if not boxURI in uriList:
												uriList.append(boxURI)
							return uriList
						uriList = findBoxes(tree, uriList)
						for boxURI in uriList:
							boxObject = AS.getContainer(session, boxURI, loginData)
							for location in coordinateList:
								locationURI = AS.findLocation(session, location["Title"], loginData)
								locFound = False
								if len(boxObject.container_locations) > 0:
									for listedLoc in boxObject.container_locations:
										if listedLoc["ref"] == locationURI:
											locFound = True
								if locFound == False:
									boxUpdates = True
									locationObject = AS.getLocation(session, locationURI, loginData)
									if len(coordinateList) > 1:
										locationObject.temporary = "collection_level"
										post0 = AS.postLocation(session, locationObject, loginData)
										if post0 != 200:
											print ("location:" + str(post0))
										boxObject = AS.addToLocation(boxObject, locationURI, location["Note"], "previous", "2999-01-01")
									else:
										boxObject = AS.addToLocation(boxObject, locationURI)
							post1 = AS.postContainer(session, repo, boxObject, loginData)
							if post1 != 200:
								print ("container: " + str(post1))	
							
				
			else:
				#multiple locations
				coordinateList = []
				for place in str(locationCode).split(";"):
					print place
					print "\n"
					coordinates = uaLocations.location2ASpace(place.strip())
					if coordinates[1] is True:
						for coordSet in coordinates[0]:
							coordinateList.append(coordSet)
					else:
						coordinateList.append(coordinates[0])
				print coordinateList
				print "\n\n"
				collectionObject = AS.getResourceID(session, repo, ID, loginData)
				#take this out before production migration
				if collectionObject is None:
					pass
				else:
					hasChildren = False
					tree = AS.getTree(session, collectionObject, loginData)
					for child in tree.children:
						if not "website" in child.title.lower() and not "web archives" in child.title.lower():
							hasChildren = True
					if hasChildren == False:
						boxObject = AS.makeContainer(session, repo, "Collection", "X", loginData)
						for location in coordinateList:
							locationURI = AS.findLocation(session, location["Title"], loginData)
							locFound = False
							if len(boxObject.container_locations) > 0:
								for listedLoc in boxObject.container_locations:
									if listedLoc["ref"] == locationURI:
										locFound = True
							if locFound == False:
								boxUpdates = True
								locationObject = AS.getLocation(session, locationURI, loginData)
								if len(coordinateList) > 1:
									locationObject.temporary = "collection_level"
									post0 = AS.postLocation(session, locationObject, loginData)
									if post0 != 200:
										print ("location:" + str(post0))
									boxObject = AS.addToLocation(boxObject, locationURI, location["Note"], "previous", "2999-01-01")
								else:
									boxObject = AS.addToLocation(boxObject, locationURI)
						post1 = AS.postContainer(session, repo, boxObject, loginData)
						if post1 != 200:
							print (post1)
						collectionObject = AS.addToContainer(session, collectionObject, boxObject.uri, None, None, loginData)
						post2 = AS.postResource(session, repo, collectionObject, loginData)			
						if post2 != 200:
							print (post2)
					else:
						uriList = []
						def findBoxes(tree, uriList):
							for child in tree.children:			
								if len(child.containers) < 1:
									findBoxes(child, uriList)
								else:
									aoObject = AS.getArchObj(session, child.record_uri, loginData)
									for box in aoObject.instances:
										if "sub_container" in box.keys():
											boxURI = box.sub_container.top_container.ref
											if not boxURI in uriList:
												uriList.append(boxURI)
							return uriList
						uriList = findBoxes(tree, uriList)
						boxUpdates = False
						for boxURI in uriList:
							boxObject = AS.getContainer(session, boxURI, loginData)
							for location in coordinateList:
								locationURI = AS.findLocation(session, location["Title"], loginData)
								locFound = False
								if len(boxObject.container_locations) > 0:
									for listedLoc in boxObject.container_locations:
										if listedLoc["ref"] == locationURI:
											locFound = True
								if locFound == False:
									boxUpdates = True
									locationObject = AS.getLocation(session, locationURI, loginData)
									if len(coordinateList) > 1:
										locationObject.temporary = "collection_level"
										post0 = AS.postLocation(session, locationObject, loginData)
										if post0 != 200:
											print ("location:" + str(post0))
										boxObject = AS.addToLocation(boxObject, locationURI, location["Note"], "previous", "2999-01-01")
									else:
										boxObject = AS.addToLocation(boxObject, locationURI)
							if boxUpdates == True:
								boxName = boxObject.display_string
								post1 = AS.postContainer(session, repo, boxObject, loginData)
								print "	-->posted " + str(boxName)
								if post1 != 200:
									print ("container:" + str(post1))
								collectionObject = AS.addToContainer(session, collectionObject, boxObject.uri, None, None, loginData)
						