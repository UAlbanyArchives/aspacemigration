import os
import csv
from archives_tools import aspace as AS

__location__ = os.path.dirname(os.path.realpath(__file__))

accessionFile = open(os.path.join(__location__, "cmsExports", "tblAccession20170405.csv"), "r")

loginData = AS.getLogin()
#loginData = ("http://localhost:8089", "admin", "admin")
session = AS.getSession(loginData)

aCount = 0
aEmptyCount = 0
collectionName = ""
for accession in csv.DictReader(accessionFile, delimiter='|'):
	if len(accession["collection_id"]) < 1:
		aEmptyCount = aEmptyCount + 1
	else:
		aCount = aCount + 1
		aNumber= accession["accession_number"].strip()
		aIDraw = accession["collection_id"]
		aID = aIDraw.replace("-", "").lower()
		
		#get collection table data
		collectionFile = open(os.path.join(__location__, "cmsExports", "tblCollection20170405.csv"), "r")
		for collection in csv.DictReader(collectionFile, delimiter='|'):
			if collection["collection_id"] == aIDraw:
				collectionName = collection["title"]
				presNote = collection["preservation_note"]
				restrictNote = collection["restriction"]
		collectionFile.close()
		
		aObject = AS.makeAccession()
		
		if len(accession["acquisition_dt"]) > 0:
			aDate = accession["acquisition_dt"].split(" ")[0].strip()
		else:
			aDate = accession["update_date"].split(" ")[0].strip()
		updateDate =  accession["update_date"].split(" ")[0].strip()
		createTime = accession["update_date"].replace(" ", "T").strip()
		if "." in createTime:
			createTime = createTime.split(".")[0]
		aObject.create_time = createTime + "Z"
		
		aObject.id_0 = aNumber
		aObject.title = collectionName
		aObject.accession_date = aDate
		aObject.general_note = "Record migrated from old CMS, last updated there: " + accession["update_date"].strip()
		
		if len(presNote) > 0:
			aObject.condition_description = presNote
		if len(restrictNote) > 0:
			aObject.restrictions_apply = True
			aObject.access_restrictions = True
			aObject.access_restrictions_note = restrictNote
			
		if len(accession["donor_note"]) > 0:
			aObject.content_description = accession["donor_note"]
		
		#provenance field
		provText = ""
		if len(accession["donor_name"]) > 0:
			provText = provText + "Donor Name: " + accession["donor_name"]
		if len(accession["institution"]) > 0:
			provText = provText + "\nInstitution: " + accession["institution"]
		if len(accession["address"]) > 0:
			provText = provText + "\nAddress:\n" + accession["address"]
		if len(accession["city"]) > 0:
			provText = provText + "\n" + accession["city"] + ", " + accession["state"] + " " + accession["zip"]
		if len(accession["home_phone"]) > 0:
			provText = provText + "\n" + accession["home_phone"]
		if len(accession["work_phone"]) > 0:
			provText = provText + "\n" + accession["work_phone"]
		if len(accession["email"]) > 0:
			provText = provText + "\n" + accession["email"]
		if len(provText) > 0:
			aObject.provenance = provText
		
		volume = accession["volume"]
		if len(volume) > 0:
			if "cu. ft." in volume:
				extent = volume.replace("cu. ft.", "").strip()
			elif "cubic ft." in volume:
				extent = volume.replace("cubic ft.", "").strip()
			elif "cubic feet" in volume:
				extent = volume.replace("cubic feet", "").strip()
			else:
				extent = volume
				
			try:
				float(extent)
				cubicFt = True
			except:
				cubicFt = False
			
			if cubicFt == True:
				AS.makeExtent(aObject, extent, "cubic ft.")
			else:
				if "volume" in volume:
					extent = volume.replace("volume", "").strip()
				elif "volumes" in volume:
					extent = volume.replace("volumes", "").strip()
				try:
					float(extent)
					volumeCheck = True
				except:
					volumeCheck = False
				if volumeCheck == True:
					AS.makeExtent(aObject, extent, "vol.")
				else:
					AS.makeExtent(aObject, volume, "uncontrolled")

		
		noResourceList = []
		alreadyFound = {}
		#if aCount == 999 or aCount == 998:
		print ("looking for " + aID)
		resourceSwitch = False
		try:
			collection = AS.getResourceID(session, "2", aID, loginData)
			print ("found " + collection.title)
			resourceSwitch = True
			#print (collection.uri)
			uriLink = {"ref":  collection.uri}
			aObject.related_resources.append(uriLink)
		except:
			try:
				collection = AS.getResourceID(session, "2",  aID, loginData)
				print ("found " + collection.title)
				resourceSwitch = True
				#print (collection.uri)
				uriLink = {"ref":  collection.uri}
				aObject.related_resources.append(uriLink)
			except:
				if aID in alreadyFound.keys():
					alreadyFoundURI = alreadyFound[aID]
					resourceSwitch = True
					uriLink = {"ref": alreadyFoundURI}
					aObject.related_resources.append(uriLink)
				else:
					print ("	" + aID + " not in index, trying longer request...")
					for collection in AS.getResources(session, "2", "all", loginData):
						if collection.id_0.endswith(aID):
							print ("found " + collection.title)
							alreadyFound.update({aID: collection.uri})
							resourceSwitch = True
							#print (collection.uri)
							uriLink = {"ref":  collection.uri}
							aObject.related_resources.append(uriLink)
		#AS.pp(aObject)
		AS.postAccession(session, "2", aObject, loginData)
		print ("posted accession --->" + str(aCount))
		if resourceSwitch == False:
			noResourceList.append(aID)
		
file = open("error.log", "a")
for item in noResourceList:
	file.write("%s\n" % item)
file.close()

file2 = open("noIndex.log", "a")
for uri in alreadyFound:
	file2.write("%s\n" % uri)
file2.close()

print (aCount)
print (aEmptyCount)

accessionFile.close()