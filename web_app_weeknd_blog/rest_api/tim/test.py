import requests

BASE = "http://127.0.0.1:5000/"


data = [{"name": "tim", "views": 777, "likes": 134},
		{"name": "kim", "views": 23, "likes": 14},
		{"name": "jom", "views": 34, "likes": 1}]

for i in range (len(data)):
	response = requests.put(BASE + "video/" + str(i), data[i])
	print (response.json())


input ()
response = requests.delete(BASE + "video/0")
print (response)

input ()
response = requests.patch(BASE + "video/2", {"views": 99, "likes": 101})
print (response.json())
