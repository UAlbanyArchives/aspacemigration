import os
import csv

__location__ = os.path.dirname(os.path.realpath(__file__))

accessionFile = open(os.path.join(__location__, "cmsExports", "tblAccession20170405.csv"), "r")

numberList = []
lineCount = 0
for accession in csv.DictReader(accessionFile, delimiter='|'):
	lineCount = lineCount + 1
	aNumber= accession["accession_number"].strip()
	if aNumber in numberList:
		print "Dup accession number " + str(aNumber) + " on line " + str(lineCount)
	else:
		numberList.append(aNumber)
	


accessionFile.close()