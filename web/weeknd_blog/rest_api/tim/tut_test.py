import requests

BASE = "http://127.0.0.1:5000/"
# response = requests.get(BASE + "helloworld")
response = requests.post (BASE + "helloworld")
# response = requests.get(BASE + "helloworld/tim/19")
#response = requests.get(BASE + "helloworld/ben")

print (response.json())
