from flask import Flask, render_template
app = Flask(__name__)

@app.route ('/x')
def hello ():
	return render_template ('xindex.html')

@app.route ('/xabout')
def about ():
	name = 'real gone'
	return render_template ('xabout.html', n = name)

@app.route ('/bootstrap')
def bootstrap ():
	return render_template ('bootstrap_starter.html')


app.run (debug = True)
