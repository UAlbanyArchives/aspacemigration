# -*- coding: utf-8 -*-

from lxml import etree as ET
from operator import itemgetter
import os
import copy
import requests
import time
import string
import csv

__location__ = os.path.dirname(os.path.realpath(__file__))

#lxml parser for parsing XML files from strings
parser = ET.XMLParser(remove_blank_text=True)


#static pages directory on public webserver
staticDir = "\\\\romeo\\wwwroot\\eresources\\static"
dataDir = os.path.join(__location__, "staticData")

#load basic HTML template file
templateFile = os.path.join(staticDir, "templates", "template.html")
tempateInput = ET.parse(templateFile, parser)
tempate = tempateInput.getroot()

#add additional JS file for fixed header
affixHead = ET.Element("script")
affixHead.set("type", "text/javascript")
affixHead.set("src", "http://library.albany.edu/speccoll/findaids/eresources/static/js/headerAffix.js")
tempate.find("head").append(affixHead)



#############################################################
#load and parse specific templates for each static page
alpha = copy.copy(tempate)
alpha.find("head/title").text = "A-Z Complete List of Collections"
alphaContent = alpha.find("body/div[@id='mainContent']")
alphaTemplateFile = os.path.join(staticDir, "templates", "browseAlpha.xml")
alphaTempateInput = ET.parse(alphaTemplateFile, parser)
alphaTempate = alphaTempateInput.getroot()
alphaContent.append(alphaTempate)

apap = copy.copy(tempate)
apap.find("head/title").text = "New York State Modern Political Archive"
apapContent = apap.find("body/div[@id='mainContent']")
apapTemplateFile = os.path.join(staticDir, "templates", "browseAPAP.xml")
apapTempateInput = ET.parse(apapTemplateFile, parser)
apapTempate = apapTempateInput.getroot()
apapContent.append(apapTempate)

ger = copy.copy(tempate)
ger.find("head/title").text = u"German and Jewish Intellectual Émigré"
gerContent = ger.find("body/div[@id='mainContent']")
gerTemplateFile = os.path.join(staticDir, "templates", "browseGER.xml")
gerTempateInput = ET.parse(gerTemplateFile, parser)
gerTempate = gerTempateInput.getroot()
gerContent.append(gerTempate)

mss = copy.copy(tempate)
mss.find("head/title").text = u"Business, Literary, and Miscellaneous Manuscripts"
mssContent = mss.find("body/div[@id='mainContent']")
mssTemplateFile = os.path.join(staticDir, "templates", "browseMSS.xml")
mssTempateInput = ET.parse(mssTemplateFile, parser)
mssTempate = mssTempateInput.getroot()
mssContent.append(mssTempate)

ua = copy.copy(tempate)
ua.find("head/title").text = u"University Archives"
uaContent = ua.find("body/div[@id='mainContent']")
uaTemplateFile = os.path.join(staticDir, "templates", "browseUA.xml")
uaTempateInput = ET.parse(uaTemplateFile, parser)
uaTempate = uaTempateInput.getroot()
uaContent.append(uaTempate)

subjects = copy.copy(tempate)
subjects.find("head/title").text = u"Subjects"
subjectsContent = subjects.find("body/div[@id='mainContent']")
subjectsTemplateFile = os.path.join(staticDir, "templates", "browseSubjects.xml")
subjectsTempateInput = ET.parse(subjectsTemplateFile, parser)
subjectsTempate = subjectsTempateInput.getroot()
subjectsContent.append(subjectsTempate)
#############################################################



#############################################################
#Functions to make each component of static pages
#############################################################
def makePanel(id, title, date, extent, abstract, link):
	panel = ET.Element("div")
	panel.set("class", "panel panel-default")
	panelHead = ET.Element("div")
	panelHead.set("class", "panel-heading")
	panelTitle = ET.Element("div")
	panelTitle.set("class", "panel-title pull-left")
	panelBody = ET.Element("div")
	panelBody.set("class", "panel-body")
	h3 = ET.Element("h3")
	h5 = ET.Element("h5")
	quantity = ET.Element("p")
	strong = ET.Element("strong")
	strong.text = "Quantity:"
	
	
	p = ET.Element("p")
	
	h3.text = title.split(";")[0]
	if ";" in title:
		h5.text = str(title.split(";")[1]) + ", " + str(date)
	else:
		h5.text = str(date)
	if "cubic ft." in extent.lower():
		strong.tail = " " + str(extent) + " (about " + str(extent.split(" ")[0]) + " boxes)"
	else:
		strong.tail = " " + str(extent)
	p.text = abstract
	
	if len(link) > 0:
		collectionLink = ET.Element("a")
		collectionLink.set("href", link)
		collectionLink.append(panelTitle)
		panelHead.append(collectionLink)
	else:
		panelHead.append(panelTitle)
		requestButton = ET.Element("button")
		requestButton.set("class", "btn btn-primary requestModel pull-right")
		requestButton.set("id", id + ": " + title)
		requestButton.set("type", "button")
		requestButton.set("data-toggle", "modal")
		requestButton.set("data-target", "#requestBrowse")
		icon = ET.Element("i")
		icon.set("class", "glyphicon glyphicon-folder-close")
		panelHead.append(requestButton)
		requestButton.append(icon)
		icon.tail = " Request"
		
	clearFloat = ET.Element("div")
	clearFloat.set("style", "clear:both;")
	panelHead.append(clearFloat)
	panel.append(panelHead)
	panelTitle.append(h3)
	panelTitle.append(h5)
	quantity.append(strong)
	panelBody.append(quantity)
	panelBody.append(p)
	panel.append(panelBody)
	return panel
	

def makeAbstract(collection, pageContent):
	id = collection[0]
	title = collection[2]
	date = collection[3]
	extent = collection[4]
	abstract = collection[5]
	if collection[1] == "True":
		link = "http://meg.library.albany.edu:8080/archive/view?docId=" + id + ".xml"
		
		panel = makePanel(id, title, date, extent, abstract, link)
		collectionAnchor = ET.Element("a")
		collectionAnchor.set("name", id)
		collectionAnchor.set("class", "anchor")
		pageContent.append(collectionAnchor)
		pageContent.append(panel)
		return pageContent
	else:
		panel = makePanel(id, title, date, extent, abstract, "")
		collectionAnchor = ET.Element("a")
		collectionAnchor.set("name", id)
		collectionAnchor.set("class", "anchor")
		pageContent.append(collectionAnchor)
		pageContent.append(panel)
		return pageContent
		
def makeLink(collection, pageContent):
	id = collection[0]
	title = collection[2]
	date = collection[3]
	extent = collection[4]
	abstract = collection[5]
	if collection[1] == "True":
		link = "http://meg.library.albany.edu:8080/archive/view?docId=" + id + ".xml"
	else:
		if id.startswith("apap"):
			link = "http://library.albany.edu/speccoll/findaids/eresources/static/apap.html#" + id
		elif id.startswith("ger"):
			link = "http://library.albany.edu/speccoll/findaids/eresources/static/ger.html#" + id
		elif id.startswith("mss"):
			link = "http://library.albany.edu/speccoll/findaids/eresources/static/mss.html#" + id
		elif id.startswith("ua"):
			link = "http://library.albany.edu/speccoll/findaids/eresources/static/ua.html#" + id

	alphaLink = ET.Element("a")
	alphaLink.set("href", link)
	alphaLink.set("class", "alphaLink")
	alphaLink.text = str(title) + ", " + str(date)
	pageContent.append(alphaLink)
	br = ET.Element("br")
	pageContent.append(br)
	return pageContent


	
def alphaNav(contentDiv, collection):
	leftNav = contentDiv.find("div[@class='row no-gutter']/div[@id='browseNav']/div[@class='panel panel-default']/div[@class='nav list-group']")
	alphaContent = contentDiv.find("div[@class='row no-gutter']/div[@class='col-md-9 col-md-offset-3 alphaContent']")
	letter = collection[2][:1]
	if leftNav.find("li/a[@id='link-" + letter + "']") is None:
		navLi =ET.Element("li")
		navLink = ET.Element("a")
		navLink.set("id", "link-" + letter)
		navLi.set("class", "list-group-item")
		navLink.set("href", "#" + letter)
		navLink.text = letter.upper()
		navLi.append(navLink)
		leftNav.append(navLi)
	if alphaContent.find("div[@id='" + letter + "']") is None:
		anchor = ET.Element("div")
		anchor.set("id", letter)
		anchor.set("class", "anchor")
		alphaContent.append(anchor)
	else:
		anchor = alphaContent.find("div[@id='" + letter + "']")
	if contentDiv.find("div[@title='alphaList']") is None:
		anchor = makeAbstract(collection, anchor)
	else:
		alphaContent = makeLink(collection, alphaContent)
	return contentDiv
	
#############################################################
#end functions to make compontent for static pages
#############################################################	

#read collection data from file
collections = []
collectionsFile = open(os.path.join(dataDir, "collections.csv"), "r", encoding='utf-8')
reader = csv.reader(collectionsFile, delimiter="|")
for line in reader:
	collections.append(line)
collectionsFile.close()

#read subject data from file
subjectData = []
subjectsFile = open(os.path.join(dataDir, "subjects.csv"), "r", encoding='utf-8')
reader = csv.reader(subjectsFile, delimiter="|")
for line in reader:
	subjectData.append(line)
subjectsFile.close()

					
# Iterate through each collection
sortedCollections = sorted(collections, key=itemgetter(2))
for collection in sortedCollections:
	if not collection[2] is None:
		print ("reading " + collection[2])
		#sort collections in to catagories by ID prefix
		alphaContent = alphaNav(alphaContent, collection)
		if collection[0].startswith("apap"):
			apapContent = alphaNav(apapContent, collection)
		elif collection[0].startswith("ger"):
			gerContent = alphaNav(gerContent, collection)
		elif collection[0].startswith("mss"):
			mssContent = alphaNav(mssContent, collection)
		elif collection[0].startswith("ua"):
			uaContent = alphaNav(uaContent, collection)
		
		
				
###################################################
#Create Static Subject Pages
###################################################

#iterate through subjects spreadsheet

sortedSubjects = sorted(subjectData, key=itemgetter(0))
for subjectRow in sortedSubjects:
	subject = str(subjectRow[0]).strip()
	leftNav = subjectsContent.find("div[@class='row no-gutter']/div[@id='browseNav']/div[@class='panel panel-default']/div[@class='nav list-group']")
	
	rightContent = subjectsContent.find("div[@class='row no-gutter']/div[@class='col-md-9 col-md-offset-3 alphaContent']")
	letter = subject[:1].upper()
	subjectNumber = subjectRow[1].split("subjects/")[1]
	
	if leftNav.find("li/a[@id='link-" + letter + "']") is None:
		navLi =ET.Element("li")
		navLink = ET.Element("a")
		navLink.set("id", "link-" + letter)
		navLi.set("class", "list-group-item")
		navLink.set("href", "#" + letter)
		navLink.text = letter.upper()
		navLi.append(navLink)
		leftNav.append(navLi)
	if rightContent.find("div[@id='" + letter + "']") is None:
		anchor = ET.Element("div")
		anchor.set("id", letter)
		anchor.set("class", "anchor")
		rightContent.append(anchor)
	else:
		anchor = rightContent.find("div[@id='" + letter + "']")
	subjectPara = ET.Element("p")
	subjectLink = ET.Element("a")
	subjectLink.text = subject
	subjectLink.set("href", "http://library.albany.edu/speccoll/findaids/eresources/static/" + subjectNumber + ".html")
	subjectPara.append(subjectLink)
	anchor.append(subjectPara)
	
	print ("creating subject page for " + subject)
						
	if subject == "Death Penalty":
		page = copy.copy(tempate)
		page.find("head/title").text = u"National Death Penalty Archive"
		pageContent = page.find("body/div[@id='mainContent']")
		pageTemplateFile = os.path.join(staticDir, "templates", "browseNDPA.xml")
		pageTempateInput = ET.parse(pageTemplateFile, parser)
		pageTempate = pageTempateInput.getroot()
		pageContent.append(pageTempate)
	else:
		page = copy.copy(tempate)
		page.find("head/title").text = subject
		pageContent = page.find("body/div[@id='mainContent']")
		pageTemplateFile = os.path.join(staticDir, "templates", "browseSubjects.xml")
		pageTempateInput = ET.parse(pageTemplateFile, parser)
		pageTempate = pageTempateInput.getroot()
		pageTempate.find("div/div[@class='jumbotron']/h2").text = subject
		pageContent.append(pageTempate)
						
	
	
			
	for collection in sortedCollections:
		subjectIndex = 0
		if collection[0] in subjectRow:			
												
			leftNav = pageContent.find("div[@class='row no-gutter']/div[@id='browseNav']/div[@class='panel panel-default']/div[@class='nav list-group']")
			rightContent = pageContent.find("div[@class='row no-gutter']/div[@class='col-md-9 col-md-offset-3 alphaContent']")
			letter = collection[2][:1]
			
			
			if leftNav.find("li/a[@id='link-" + letter + "']") is None:
				navLi =ET.Element("li")
				navLink = ET.Element("a")
				navLink.set("id", "link-" + letter)
				navLi.set("class", "list-group-item")
				navLink.set("href", "#" + letter)
				navLink.text = letter.upper()
				navLi.append(navLink)
				leftNav.append(navLi)
			if rightContent.find("div[@id='" + letter + "']") is None:
				anchor = ET.Element("div")
				anchor.set("id", letter)
				anchor.set("class", "anchor")
				rightContent.append(anchor)
			else:
				anchor = rightContent.find("div[@id='" + letter + "']")
			
			anchor = makeAbstract(collection, anchor)

	#write static subject pages
	pageString = ET.tostring(page, pretty_print=True, method='html', xml_declaration=False, doctype="<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">")
	pageFile = open(os.path.join(staticDir, subjectNumber + ".html"), "wb")
	pageFile.write(pageString)
	pageFile.close()
	
			
			
	
#Write static pages to web server
apapString = ET.tostring(apap, method='html', xml_declaration=False, doctype="<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">")
apapFile = open(os.path.join(staticDir, "apap.html"), "wb")
apapFile.write(apapString)
pageFile.close()

gerString = ET.tostring(ger, method='html', xml_declaration=False, doctype="<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">")
gerFile = open(os.path.join(staticDir, "ger.html"), "wb")
gerFile.write(gerString)
pageFile.close()

mssString = ET.tostring(mss, method='html', xml_declaration=False, doctype="<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">")
mssFile = open(os.path.join(staticDir, "mss.html"), "wb")
mssFile.write(mssString)
pageFile.close()

uaString = ET.tostring(ua, method='html', xml_declaration=False, doctype="<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">")
uaFile = open(os.path.join(staticDir, "ua.html"), "wb")
uaFile.write(uaString)
pageFile.close()

subjectsString = ET.tostring(subjects, method='html', xml_declaration=False, doctype="<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">")
subjectsFile = open(os.path.join(staticDir, "subjects.html"), "wb")
subjectsFile.write(subjectsString)
pageFile.close()

alphaString = ET.tostring(alpha, method='html', xml_declaration=False, doctype="<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">")
alphaFile = open(os.path.join(staticDir, "alpha.html"), "wb")
alphaFile.write(alphaString)
pageFile.close()