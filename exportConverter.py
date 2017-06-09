# -*- coding: utf-8 -*-
from lxml import etree as ET


#{urn:isbn:1-931666-22-9}
def eadExportConverter(outputPath):

	parser = ET.XMLParser(remove_blank_text=True)
	ead = ET.parse(outputPath, parser)
	root = ead.getroot()
	
	ns = "{urn:isbn:1-931666-22-9}"
	
	def phydescFix(cmptn, ns):
		physdescCount = 0
		for physdesc in cmptn:
			if physdesc.tag == ns + "physdesc":
				regularSwitch = False
				daoSwitch = False
				webSwitch = False
				facetSwitch = False
				
				if not physdesc.find(ns + "extent") is None:
					if physdesc.find(ns + "extent").text.endswith("Digital Files"):
						daoSwitch = True
						daoExtent = physdesc.find(ns + "extent").text.split("Digital Files")[0].strip()
						physdesc.remove(physdesc.find(ns + "extent"))
					elif physdesc.find(ns + "extent").text.lower().endswith("captures"):
						webSwitch = True
						webExtent = physdesc.find(ns + "extent").text.split(" ")[0].strip()
						physdesc.remove(physdesc.find(ns + "extent"))
					elif physdescCount > 1:
						physdescCount = physdescCount + 1
						facetSwitch = True
						facetText = physdesc.find(ns + "extent").text
						physdesc.remove(physdesc.find(ns + "extent"))
					else:
						physdescCount = physdescCount + 1
						regularSwitch = True
						regularExtent = physdesc.find(ns + "extent").text
						physdesc.remove(physdesc.find(ns + "extent"))
				
				extentCount = 0
				for extent in physdesc:
					if extent.tag == ns + "extent":
						extentCount = extentCount + 1
						if "uncontrolled" in extent.text:
							extent.text =  extent.text.replace("uncontrolled", "")
						if extentCount > 1:
							if extent.text.endswith("Digital Files"):
								daoSwitch = True
								daoExtent = extent.text.split("Digital Files")[0].strip()
							else:
								facetSwitch = True
								facetText = physdesc.find(ns + "extent").text
							physdesc.remove(extent)
				if regularSwitch == True:
					regular = ET.Element(ns + "extent")
					regular.text = regularExtent.split(" ")[0]
					regular.set("unit",  regularExtent.split(" ")[1])
					cmptn.find(ns +"physdesc").append(regular)
				if daoSwitch == True:
					dimen = ET.Element(ns + "dimensions")
					dimen.text = daoExtent
					dimen.set("unit", "Digital Files")
					cmptn.find(ns +"physdesc").append(dimen)
				if webSwitch == True:
					facetElement = ET.Element(ns + "physfacet")
					facetElement.text = webExtent + " Captures"
					cmptn.find(ns +"physdesc").append(facetElement)
				if facetSwitch == True:
					facetElement = ET.Element(ns + "physfacet")
					facetElement.text = facetText
					cmptn.find(ns +"physdesc").append(facetElement)
			
			physChildCount = 0
			for childTag in physdesc:
				physChildCount += 1
			if physChildCount == 0:
				cmptn.remove(physdesc)
				
	
	def c0Numbers(element, ns, level):
		for child in element:
			if child.tag == (ns + "c"):
				child.tag = ns + "c0" + str(level)
				#phydescFix(child.find(ns + "did"), ns)
				c0Numbers(child, ns, level + 1)
	
	did =  root.find("{urn:isbn:1-931666-22-9}archdesc/{urn:isbn:1-931666-22-9}did")
	root.set("id", did.find(ns + "unitid").text)
	print (root.attrib["id"])
	oldDate = did.find(ns +"unitdate")
	titleElement = did.find(ns +"unittitle")
	titleElement.append(oldDate)
	
	for child in did:
		if child.tag == ns + "langmaterial":
			if child.text is None:
				did.remove(child)
	
	phydescFix(did, ns)

	c0Numbers(root.find(ns + "archdesc/" + ns + "dsc"), ns, 1)
	
	dsc =  root.find("{urn:isbn:1-931666-22-9}archdesc/{urn:isbn:1-931666-22-9}dsc")
	childCount = 0
	for cChild in dsc.findall("."):
		childCount = childCount + 1
	if childCount == 0 :
		root.find("{urn:isbn:1-931666-22-9}archdesc").remove(dsc)
	
	
	output_string = ET.tostring(root, pretty_print=True, xml_declaration=True, encoding="utf-8")
			
	file = open(outputPath, "wb")
	file.write(output_string)
	file.close()