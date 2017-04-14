# -*- coding: utf-8 -*-
import os
from archives_tools import aspace  as AS
from archives_tools import dacs
from exportConverter import eadExportConverter
import time
import csv
import shutil
from subprocess import Popen, PIPE, STDOUT

__location__ = os.path.dirname(os.path.realpath(__file__))

try:
	timePath = os.path.join(__location__, "lastExport.txt")
	with open(timePath, 'r') as timeFile:
		startTime = int(timeFile.read().replace('\n', ''))
		timeFile.close()
except:
	startTime = 0
	
#loginData = ("http://localhost:8089", "admin", "admin")
loginData = AS.getLogin()
repo = "2"

output_path = "\\\\romeo\\Collect\\spe\\Tools\\collections"
xtf_path = "\\\\zeta\\xtf\\dataTemp"
pdf_path = os.path.join('\\\\romeo\\wwwroot\\eresources\\static', 'pdf')
staticData = os.path.join(__location__, "staticData")

session = AS.getSession(loginData)

#read existing exported collection data
collectionData = []
collectionFile = open(os.path.join(staticData, "collections.csv"), "r", encoding='utf-8')
for line in csv.reader(collectionFile, delimiter="|"):
	collectionData.append(line)
collectionFile.close()


#read existing exported subject data
subjectData = []
subjectFile = open(os.path.join(staticData, "subjects.csv"), "r", encoding='utf-8')
for line in csv.reader(subjectFile, delimiter="|"):
	subjectData.append(line)
subjectFile.close


for collection in AS.getResourcesSince(session, repo, startTime, loginData):

	if collection.publish == True: 
	
		normalName = collection.finding_aid_title
		
		checkAbstract = False
		checkAccessRestrict = False
		checkDACS = [False, False, False, False, False]
		accessRestrict = ""
		
		for note in collection.notes:
			if "type" in note.keys():
				if note.type == "abstract":
					checkAbstract = True
					abstract = note.content[0].replace("\n", "&#13;&#10;")
				if note.type == "accessrestrict":
					checkAccessRestrict = True
					for subnote in note.subnotes:
						accessRestrict = "&#13;&#10;" + subnote.content.replace("\n", "&#13;&#10;")
					accessRestrict = accessRestrict.strip()
				if note.type == "acqinfo":
					checkDACS[0] = True
				if note.type == "bioghist":
					checkDACS[1] = True
				if note.type == "scopecontent":
					checkDACS[2] = True
				if note.type == "arrangement":
					checkDACS[3] = True
					
					
		for agent in collection.linked_agents:
			if agent.role == "creator":
				checkDACS[4] = True
				
		if checkAbstract == True:
			print ("exporting " + collection.title)
			date = ""
			for dateData in collection.dates:
				if "expression" in dateData.keys():
					date = dateData.expression
				else:
					if "end" in dateData.keys():
						normalDate = dateData.begin + "/" + dateData.end
					else:
						normalDate = dateData.begin
					date = dacs.iso2DACS(normalDate)
			extent = ""
			for extentData in collection.extents:
				extent = extentData.number + " " + extentData.extent_type

			ID = collection.id_0.lower().strip()
			checkCollection = False
			for existingCollection in collectionData:
				if existingCollection[0] == ID:
					existingCollection[0] = ID
					existingCollection[1] = all(checkDACS)
					existingCollection[2] = normalName
					existingCollection[3] = date
					existingCollection[4] = extent
					existingCollection[5] = abstract
					existingCollection[6] = collection.restrictions
					existingCollection[7] = accessRestrict
					checkCollection = True
			if checkCollection == False:
				collectionData.append([ID, all(checkDACS), normalName, date, extent, abstract, collection.restrictions, accessRestrict])

			for subjectRef in collection.subjects:
				subject = AS.getSubject(session, subjectRef.ref, loginData)
				if subject.source == "meg":
					if subject.terms[0].term_type == "topical":
						checkSubject = False
						for existingSubject in subjectData:
							if existingSubject[0] == subject.title:
								if not ID in existingSubject:
									existingSubject.append(ID)
								checkSubject = True
						if checkSubject == False:
							subjectData.append([subject.title, subjectRef.ref, ID])


			if all(checkDACS) == True:
				eadFile = AS.exportResource(session, repo, collection, output_path, loginData)
				eadExportConverter(eadFile)
				shutil.copy2(eadFile, xtf_path)
				pdfFile = AS.exportPDF(session, repo, collection, pdf_path, loginData)

#commit changes to git repo
addCmd = ["git", "-C", output_path, "add", "*"]
gitAdd = Popen(addCmd, stdin=PIPE)
gitAdd.communicate()
commitCmd = ["git", "-C", output_path, "commit", "-m", "modified collections exported from ArchivesSpace"]
gitCommit = Popen(commitCmd, stdin=PIPE)
gitCommit.communicate()
pushCmd = ["git", "-C", output_path, "push", "origin", "master"]
gitPush = Popen(pushCmd, stdout=PIPE, stderr=PIPE)
gitPush.communicate()

				
#write new collection data back to file
collectionFile = open(os.path.join(staticData, "collections.csv"), "w", newline='', encoding='utf-8')
writer = csv.writer(collectionFile, delimiter='|')
writer.writerows(collectionData)
collectionFile.close()

#write new subjects data back to file
subjectFile = open(os.path.join(staticData, "subjects.csv"), "w", newline='', encoding='utf-8')
writer = csv.writer(subjectFile, delimiter='|')
writer.writerows(subjectData)
subjectFile.close()

timePath = os.path.join(__location__, "lastExport.txt")
with open(timePath, 'w') as timeFile:
	timeFile.write(str(time.time()).split(".")[0])
	timeFile.close()

	
#wait 1 hour for XML to copy over to XTF on the top of every hour
"""
print ("Waiting for files to copy to XTF...")
time.sleep(900)
print ("45 minutes remaining...")
time.sleep(900)
print ("30 minutes remaining...")
time.sleep(900)
print ("15 minutes remaining...")
time.sleep(900)
"""
msg = "Calling script to generate static pages..."
print (msg)

staticPages = os.path.join(__location__, "staticPages.py")

#build command list
staticCmd = ["python", "staticPages.py"]
makeStatic = Popen(staticCmd, stdout=PIPE, stderr=PIPE)
stdout, stderr = makeStatic.communicate()
if len(stdout) > 0:
	print (stdout)
if len(stderr) > 0:
	print ("ERROR: staticPages.py failed. " + str(stderr))
else:
	print ("Export Complete")