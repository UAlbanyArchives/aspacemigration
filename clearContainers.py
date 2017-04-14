from archives_tools import aspace as AS

loginData = AS.getLogin()
session = AS.getSession(loginData)
repo = "2"

count = 0
box = "start"
start = 1
end = 50
while (box != None):
	range = str(start) + "-" + str(end)
	print range
	for box in AS.getContainers(session, repo, range, loginData):
		count = count + 1
		if len(box.container_locations) > 0:
			box.container_locations = []
			boxURI = box.uri
			AS.postContainer(session, repo, box, loginData)
			print "posted " + str(boxURI)
	start = end + 1
	end = start + 49
	#print box
	print count
		
print "final count: " + str(count)