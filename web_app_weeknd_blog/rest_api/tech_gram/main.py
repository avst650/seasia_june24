from flask import Flask, jsonify, request

app = Flask(__name__)

books_db = [
	{
		'name': 'secrets',
		'price': 250
	},

	{
		'name': 'deep work',
		'price': 347
	}
]

########################              GET API - fetch books and book

@app.route('/')
def hello():
	return '<h1>AFTER HOURS</h1>my darkest hours, girl i felt so alone in this crowded room. Different girls try distracting my thoughts for you, i turned into the man i used to be'

@app.route('/books')
def get_all_books():
	return jsonify({'books': books_db})

@app.route('/books/<string:name>')
def get_book(name):
	for book in books_db:
		if book['name'] == name:
			return jsonify(book)

	return jsonify({'message': 'book not found'})

@app.route('/books', methods = ['POST'])
def create_book():
	body_data = request.get_json()
	books_db.append(body_data)

	return jsonify({"message": "book has been created"})


app.run(debug = True)
