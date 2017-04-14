from archives_tools import aspace as AS

repo = "2"
loginData = AS.getLogin()
session = AS.getSession(loginData)

count = 0

for collection in AS.getResources(session, repo, "all", loginData):
	count = count + 1
	ID = collection.uri
	print collection.id_0 + ": " + collection.title
	if collection.id_0.startswith("nam_"):
		newID = collection.id_0.replace("nam_", "")
		collection.id_0 = newID
		
		post = AS.postResource(session, repo, collection, loginData)
		print post

print str(count) + " total resources"