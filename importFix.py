import os
from lxml import etree as ET
from archives_tools import dacs
from datetime import datetime

eadDir = "\\\\romeo\\Collect\\spe\\Tools\\collections"
outDir = "C:\\Projects\\aspaceImportData"
webDir = "C:\\Projects\\aspaceAPI\\ASpace_WebArchives\\webArchEADs"

parser = ET.XMLParser(remove_blank_text=True)

for eadFile in os.listdir(eadDir):
	webArch = False
	if eadFile.endswith(".xml"):
		if 1== 1:
			#print "reading " + eadFile
			FA_input = ET.parse(os.path.join(eadDir, eadFile), parser)
			FA = FA_input.getroot()
		
			print eadFile
			
			if FA.find("archdesc/phystech") is None:
				pass
			elif FA.find("archdesc/phystech/p").text.lower() == "web archives":
				webArch = True
			
			colID = FA.find("eadheader/eadid").text
			if "_" in colID:
				colID = colID.split("_")[1]
				FA.find("eadheader/eadid").set("url", "http://meg.library.albany.edu:8080/archive/view?docId=" + colID + ".xml")
				FA.find("eadheader/eadid").text = colID
			if "_" in FA.attrib["id"]:
				dropNAM = FA.attrib["id"].split("_")[1]
				FA.set("id", dropNAM)
			
			elementList = FA.findall(".//")
			for element in reversed(elementList):
				if element.text is None or element.text == " ":
					if len(element.getchildren()) < 1:
						if not element.tag == "dao":
							element.getparent().remove(element)
						else:
							if element.getparent().tag != "did":
								pass
							else:
								if element.getparent().find("unittitle").text is None:
									if element.getparent().find("unittitle/emph").text is None:
										if element.getparent().find("unittitle/emph/emph").text is None:
											print ("dao error: " + element.getparent().getparent().attrib["id"])
										else:
											title = element.getparent().find("unittitle/emph/emph").text
											elementTitle = element.getparent().find("unittitle/emph")
											elementTitle.remove(elementTitle.find("emph"))
											elementTitle.text = title
									else:
										title = element.getparent().find("unittitle/emph").text
								else:
									title = element.getparent().find("unittitle").text
								element.set("title", title)
								
				if element.tag == "emph":
					if element.find("emph") is None:
						pass
					else:
						name = element.find("emph").text
						element.remove(element.find("emph"))
						element.text = name
						
				if element.tag == "container":
					if element.attrib["type"] == "Box":
						if element.getparent() is None:
							print element.attrib + "?"
							print element.getparent().tag + "??"
						else:
							boxParent = element.getparent().getparent().getparent()
							if boxParent.tag == "dsc":
								boxLabel = boxParent.getparent().find("did/unittitle").text[0:50]
								element.text = element.text + " (" + boxLabel + ")"
							else:
								if boxParent.tag == "c01":
									pass
								elif boxParent.tag == "c02":
									boxParent = boxParent.getparent()
								if boxParent.find("did/unittitle").text is None:
									if boxParent.find("did/unittitle/emph") is None:
										if boxParent.find("did/unittitle/title") is None: 
											print ("container error: " + boxParent.attrib["id"])
										else:
											boxLabel = boxParent.find("did/unitid").text + "-" + boxParent.find("did/unittitle/title").text[0:50]
											element.text = element.text + " (" + boxLabel + ")"
									else:
										if boxParent.find("did/unittitle/emph").text is None:
											print ("container error: " + boxParent.attrib["id"])
										else:
											boxLabel = boxParent.find("did/unitid").text + "-" + boxParent.find("did/unittitle/emph").text[0:50]
											element.text = element.text + " (" + boxLabel + ")"
								else:
									boxLabel = boxParent.find("did/unitid").text + "-" + boxParent.find("did/unittitle").text[0:50]
									element.text = element.text + " (" + boxLabel + ")"
				
				if element.tag == "unitdate":
					if not "normal" in element.attrib:
						if element.getparent().getparent().tag == "archdesc":
							print "collection date error"
						else:
							try:
								print "DATE ERROR2: " + element.getparent().getparent().attrib["id"]
							except:
								print element.getparent().tag
								print eadFile + "????"
					else:
						normalDate = element.attrib["normal"].strip()
						element.set("normal", normalDate)
						if "/" in normalDate:
							if normalDate.split("/")[1] < normalDate.split("/")[0]:
								print "DATE ERROR: " + element.getparent().getparent().attrib["id"]
							else:
								try:
									if normalDate.split("/")[0].count('-') == 2:
										datetime.strptime(normalDate.split("/")[0], '%Y-%m-%d')
									elif normalDate.split("/")[0].count('-') == 1:
										datetime.strptime(normalDate.split("/")[0], '%Y-%m')
									if normalDate.split("/")[1].count('-') == 2:
										datetime.strptime(normalDate.split("/")[1], '%Y-%m-%d')
									elif normalDate.split("/")[1].count('-') == 1:
										datetime.strptime(normalDate.split("/")[1], '%Y-%m')
								except:
									if "id" in element.getparent().getparent().attrib:
										print "DATE ERROR, INVALID: " + element.getparent().getparent().attrib["id"]
									else:
										print "DATE ERROR, odd invalid: " + element.getparent().getparent().tag + " in " + eadFile + ": " + normalDate
						else:
							try:
								if normalDate.count('-') == 2:
									datetime.strptime(normalDate, '%Y-%m-%d')
								elif normalDate.count('-') == 1:
									try:
										datetime.strptime(normalDate, '%Y-%m')
									except:
										if len(normalDate) == 9:
											normalDateFix = normalDate.replace("-", "/")
											datetime.strptime(normalDateFix.split("/")[0], '%Y')
											datetime.strptime(normalDateFix.split("/")[1], '%Y')
											element.set("normal", normalDateFix)
										else:
											raise ValueError("Normal date still invalid after replacing - with /")
								else:
									datetime.strptime(normalDate, '%Y')
							except:
								if eadFile == "apap196.xml":
									if normalDate[5] == "-":
										normalDateFix = normalDate.split("-")[2] + "-" + normalDate.split("-")[1] + "-" + normalDate.split("-")[0]
									elif normalDate[2] == "-":
										normalDateFix = normalDate[3:] + "-" + normalDate.split("-")[0]
										
									try:
										if normalDate.count('-') == 2:
											datetime.strptime(normalDateFix, '%Y-%m-%d')
										elif normalDate.count('-') == 1:
											datetime.strptime(normalDateFix, '%Y-%m')
										element.set("normal", normalDateFix)
									except:
										print "DATE ERROR, INVALID: " + element.getparent().getparent().attrib["id"]
								
								
								else:
									try:
										if "id" in element.getparent().getparent().attrib:
											print "DATE ERROR, INVALID: " + element.getparent().getparent().attrib["id"]
										else:
											print "DATE ERROR, odd invalid: " + element.getparent().getparent().tag + " in " + eadFile + ": " + normalDate
									except:
										print element.tag
										print element.text
										print element.attrib
										if "id" in element.getparent().getparent().attrib:
											print "test"
								
				if element.tag == "extent":
					element.set("type", "spaceoccupied")
						
				if element.tag.startswith("c0"):
					if not "id" in element.attrib:
						if eadFile == "apap078.xml" or eadFile == "apap082.xml"or eadFile == "mss035.xml":
							element.attrib["id"] = "nam_" + element.find("did/unitid").text.split("nam_")[1]
							didFix = element.find("did")
							didFix.remove(didFix.find("unitid"))
						elif eadFile == "apap110.xml" or eadFile == "mss029.xml":
							element.set("id", element.find("did/unitid").text)
							didFix = element.find("did")
							didFix.remove(didFix.find("unitid"))
						else:
							print(element.attrib)
							print(element.tag + "???????")
							uid = element.attrib["id"]
					uid = element.attrib["id"]
					"""
					if element.find("did/unitid") is None:
						unitid = ET.Element("unitid")
						unitid.text = uid
						element.find("did").insert(0, unitid)
					else:
						element.find("did/unitid").text = uid
					"""
					element.attrib.pop("id")
						
					#print element.attrib["id"]
					if element.find("did/unittitle") is None:
						if "id" in element.attrib:
							print "UNITTITLE ERROR: " + element.attrib["id"]
						else:
							print "UNITTITLE ERROR? " + element.tag
							#print ET.tostring(element)
					elif element.find("did/unittitle").text is None and element.find("did/unittitle/emph") is None:
						if "id" in element.attrib:
							print "UNITTITLE ERROR: " + element.attrib["id"]
						else:
							print "UNITTITLE ERROR?? " + element.tag
					if element.find("did/unittitle") is None:
						pass
					elif not element.find("did/unittitle").text is None:
						if element.find("did/unittitle").text.lower().startswith("sub-series"):
							#print element.find("did/unittitle").text
							if ":" in element.find("did/unittitle").text:
								element.find("did/unittitle").text = element.find("did/unittitle").text.split(":")[1].strip()
				
					if not element.find("did/physdesc/extent") is None:
						if "unit" in element.find("did/physdesc/extent").attrib:
							element.find("did/physdesc/extent").text = element.find("did/physdesc/extent").text + " " + element.find("did/physdesc/extent").attrib["unit"]
					if not element.find("did/physdesc/dimensions") is None:
						element.find("did/physdesc/dimensions").set("type", "Digital Files")
						element.find("did/physdesc/dimensions").text = element.find("did/physdesc/dimensions").text + " Digital Files"
						element.find("did/physdesc/dimensions").tag = "extent"
						
					"""
					if element.find("did/unitdate") is None:
						print "Needed to add unitdate"
						print element.tag
						print element.find("did/unitid").text
						unitdate = ET.Element("unitdate")
						unitdate.set("type", "inclusive")
						unitdate.set("era", "ce")
						unitdate.set("calendar", "gregorian")
						unitdate.set("normal", FA.find("archdesc/did/unitdate").attrib["normal"])
						unitdate.text = "Undated"
						element.find("did").append(unitdate)
					"""
						
					
					if len(uid.split("_")) > 2:
						fileID = uid.split("_")[2]
						if "." in fileID:
							element.set("level", "item")
						else:
							element.set("level", "file")
					else:
						folderSwitch = False
						for container in element.find("did"):
							if container.tag == "container":
								if container.attrib["type"].lower() == "folder":
									folderSwitch = True
						if folderSwitch == True:
							element.set("level", "file")
							
 				
			
			for extent in FA.find("archdesc/did/physdesc"):
				if extent.tag == "extent":
					if "Reelss" in extent.text:
						extent.text = extent.text.replace("Reelss", "Reels")
					if "foldewrs" in extent.text:
						extent.text = extent.text.replace("foldewrs", "folders")
					if "cubic feet" in extent.text:
						extent.text = extent.text.replace("cubic feet", "cubic ft.")
			
			
					
					
					extent.text = extent.text + " " + extent.attrib["unit"]
					extent.attrib.pop("unit")
			if FA.find("archdesc/did/physdesc/extent") is None:
				if FA.find("archdesc/did/physdesc/physfacet") is None or FA.find("archdesc/did/physdesc/physfacet").text is None:
					if FA.find("archdesc/did/physdesc/dimensions") is None:
						print eadFile + "!!!"
				else:
					physfacet = FA.find("archdesc/did/physdesc/physfacet")
					if "microfilm reel" in physfacet.text.lower() or "microfilm reels" in physfacet.text.lower() or "daybook" in physfacet.text.lower():
						#print physfacet.text
						extentText = physfacet.text.replace("microfilm reel", "Reels").replace("microfilm reels", "Reels").replace("Microfilm Reel", "Reels").replace("Microfilm Reels", "Reels")
						FA.find("archdesc/did/physdesc").remove(physfacet)
						extent = ET.SubElement(FA.find("archdesc/did/physdesc"), "extent")
						extent.text = extentText
						
			if not FA.find("archdesc/did/physdesc/dimensions") is None:
				FA.find("archdesc/did/physdesc/dimensions").set("type", "Digital Files")
				FA.find("archdesc/did/physdesc/dimensions").text = FA.find("archdesc/did/physdesc/dimensions").text + " Digital Files"
				FA.find("archdesc/did/physdesc/dimensions").tag = "extent"
					
			FA.find("eadheader/filedesc/titlestmt").remove(FA.find("eadheader/filedesc/titlestmt/titleproper"))
			titleproper = ET.Element("titleproper")
			titleproper.text = FA.find("archdesc/did/unittitle").text
			FA.find("eadheader/filedesc/titlestmt").insert(0, titleproper)
			
			
			FA.find("eadheader/profiledesc/langusage").remove(FA.find("eadheader/profiledesc/langusage/language"))
			FA.find("eadheader/profiledesc/langusage").text = "English"
			
			if FA.find("archdesc/did/physdesc/extent") is None:
				print "EXTENT ERROR: " + eadFile
			
			
			eadDate = FA.find("eadheader/profiledesc/creation/date").attrib["normal"]
			
			processor = FA.find("eadheader/filedesc/titlestmt/author").text
			processingDate = FA.find("eadheader/filedesc/publicationstmt/date").attrib["normal"]
			
			FA.find("eadheader/filedesc/publicationstmt/date").text = dacs.iso2DACS(processingDate)
			
			processP = ET.Element("p")
			processP.text = "Processed in " + dacs.iso2DACS(processingDate) + " by " + processor + "."
			if FA.find("archdesc/processinfo") is None:
				processinfo = ET.Element("processinfo")
				processinfo.append(processP)
				FA.find("archdesc").insert(1, processinfo)
			else:
				FA.find("archdesc/processinfo").insert(0, processP)
			
			eadCreator = FA.find("eadheader/profiledesc/creation").text.strip()
			if eadCreator.endswith(","):
				eadCreator = eadCreator[:-1]
			
			if not FA.find("archdesc/scopecontent/head") is None:
				 FA.find("archdesc/scopecontent").remove(FA.find("archdesc/scopecontent/head"))
				 
			if FA.attrib["id"] == "nam_apap030":
				for para in FA.find("archdesc/bioghist"):
					for chronlist in para:
						if chronlist.tag == "chronlist":
							para.remove(chronlist)
					if len(para.getchildren()) < 1:
						para.getparent().remove(para)
						
			arrange =FA.find("archdesc/arrangement")
			if len(arrange.getchildren()) < 1:
				print FA.attrib["id"]
			pCount = 0
			for parag in arrange:
				if parag.tag == "p":
					pCount = pCount + 1
			if pCount < 1:
				newP = ET.SubElement(arrange, "p")
				newP.text = "This collection has no series."
							
			if FA.find("eadheader/revisiondesc") is None:
				revisiondesc = ET.Element("revisiondesc")
			else:
				revisiondesc = FA.find("eadheader/revisiondesc")
			change = ET.SubElement(revisiondesc, "change")
			date = ET.SubElement(change, "date")
			date.text = dacs.iso2DACS(eadDate)
			date.set("normal", eadDate)
			item = ET.SubElement(change, "item")
			item.text = "Encoded in EAD by " + eadCreator
			if FA.find("eadheader/revisiondesc") is None:
				FA.find("eadheader").append(revisiondesc)
			
			""""
			if FA.attrib["id"] == "nam_apap032":
				print "check"
				idList = []
				elementList = FA.findall(".//")
				for element in reversed(elementList):
					if element.tag.startswith("c0"):
						if element.find("did/unitid").text in idList:
							print element.find("did/unitid").text + "<-- Here"
						else:
							idList.append(element.find("did/unitid").text)
			"""
						
				
		

		
			FA_string = ET.tostring(FA, pretty_print=True, xml_declaration=True, encoding="utf-8", doctype="<!DOCTYPE ead SYSTEM 'ead.dtd'>")
			#print "writing " + eadFile
			file = open(os.path.join(outDir, eadFile), "w")
			file.write(FA_string)
			file.close()
			if webArch == True:
				file = open(os.path.join(webDir, eadFile), "w")
				file.write(FA_string)
				file.close()
				
			