from flask import Flask
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

# names = {"bill": {"age": 12, "gender": "male"},
# 		"ben": {"age": 34, "gender": "female"}}


class HelloWorld(Resource):


	# def get(self):
	# 	return {"data":"hello boi"}

	def post(self):
		return {"data": "swallow"}


	# def get(self, name, test):
		# return {"name": name, "test": test}


	# def get(self, name):
	# 	return names[name]

api.add_resource (HelloWorld, "/helloworld")
#api.add_resource (HelloWorld, "/helloworld/<string:name>/<int:test>")
# api.add_resource (HelloWorld, "/helloworld/<string:name>")

if __name__ == '__main__':
	app.run(debug = True)
