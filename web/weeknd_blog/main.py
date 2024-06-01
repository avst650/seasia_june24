from flask import Flask, render_template, request, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import datetime
import json
from werkzeug.utils import secure_filename
import os
import math

#file_path = r"C:/Users/vashistanush/OneDrive/flask2/config.json"

with open ('config.json', 'r') as c:
	params = json.load (c)["params"]

local_server = True
app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = params['upload_location']

''' app.config.update (

	MAIL_SERVER = 'smtp.gmail.com',
	MAIL_PORT = '465',
	MAIL_USE_SSL = True,
	MAIL_USERNAME = params ['gmail_user'],
	MAIL_PASSWORD = params ['gmail_pass']

)

mail = Mail (app)'''

if (local_server) == True:
	app.config['SQLALCHEMY_DATABASE_URI'] = params ['local_uri']

else:
	app.config['SQLALCHEMY_DATABASE_URI'] = params ['prod_uri']

db = SQLAlchemy (app)


class Contacts(db.Model):
	serial_number = db.Column (db.Integer, primary_key = True)
	name = db.Column (db.String (80), nullable = False)
	email = db.Column (db.String (20), nullable = False)
	phone_number = db.Column (db.String (12), nullable = False)
	message = db.Column (db.String (120), nullable = False)
	date = db.Column (db.String (12), nullable = True)

class Posts(db.Model):
	serial_number = db.Column (db.Integer, primary_key = True)
	title = db.Column (db.String (80), nullable = False)
	slug = db.Column (db.String (21), nullable = False)
	content = db.Column (db.String (200), nullable = False)
	tagline = db.Column (db.String (120), nullable = True)
	date = db.Column (db.String (12), nullable = True)
	img_file = db.Column (db.String (50), nullable = True)
	

@app.route("/")
@app.route("/home")
def home():
	
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['number_of_posts']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page-1)*int(params['number_of_posts']):(page-1)*int(params['number_of_posts'])+ int(params['number_of_posts'])]
    if page==1:
        prev = "#"
        next = "/?page="+ str(page+1)
    elif page==last:
        prev = "/?page="+ str(page-1)
        next = "#"
    else:
        prev = "/?page="+ str(page-1)
        next = "/?page="+ str(page+1)

    flash("Trilogy", "dark")
    flash("Kissland", "success")
    flash("Beauty behind madness", "dark")
    flash("Starboy", "danger")
    flash("My dear mealancholy", "warning")
    flash("After Hours", "danger")
    flash("Dawn FM", "primary")
    return render_template('index.html', params=params, posts=posts, prev=prev, next=next)

@app.route ('/about')
def about ():
	return render_template ('about.html', params= params)

@app.route ('/dashboard', methods = {'GET', 'POST'})
def dashboard ():

	if ('user' in session and session['user'] == params['admin_user']):
		posts = Posts.query.all()
		return render_template('dashboard.html', params= params, posts = posts)


	if request.method == 'POST':
		username = request.form.get('uname')
		userpass = request.form.get('pass')

		if (username == params['admin_user'] and userpass == params['admin_password']):
			#set the session variable
			session['user'] = username
			posts = Posts.query.all()
			return render_template('dashboard.html', params= params, posts = posts)


	return render_template ('login.html', params= params)

@app.route ("/post/<string:post_slug>", methods = ['GET'])
def post_route (post_slug):

	post = Posts.query.filter_by (slug = post_slug).first()

	return render_template ('post.html', params= params, post = post)

@app.route ('/edit/<string:serial_number>', methods = {'GET', 'POST'})
def edit(serial_number):
	if ('user' in session and session['user'] == params['admin_user']):
		if request.method == 'POST':
			box_title = request.form.get ('title')
			tagline = request.form.get ('tagline')
			slug = request.form.get ('slug')
			content = request.form.get ('content')
			img_file = request.form.get ('img_file')
			date = datetime.now()

			if serial_number == '0':
				post = Posts (title = box_title, tagline = tagline, slug = slug, content = content, img_file = img_file, date = date)
				db.session.add(post)
				db.session.commit()

			else:
				post = Posts.query.filter_by(serial_number = serial_number).first()
				post.title = box_title
				post.slug = slug
				post.content = content
				post.tagline = tagline
				post.img_file = img_file
				post.date = date
				db.session.commit()
				return redirect('/edit/'+serial_number)
	post = Posts.query.filter_by(serial_number = serial_number).first()

	return render_template ('edit.html', params = params, post = post, serial_number = serial_number)			


@app.route ('/uploader', methods = {'GET', 'POST'})
def uploader():
	if ('user' in session and session['user'] == params['admin_user']):
		if (request.method == 'POST'):
			f = request.files['file1']
			f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename) ))
			return "uploaded successfully"


@app.route ('/logout')
def logout():
	session.pop('user')
	return redirect('/dashboard')


@app.route ('/delete/<string:serial_number>', methods = {'GET', 'POST'})
def delete(serial_number):
	if ('user' in session and session['user'] == params['admin_user']):
		post = Posts.query.filter_by(serial_number = serial_number).first()
		db.session.delete(post)
		db.session.commit()
	return redirect('/dashboard')


@app.route ('/contact', methods = {'GET', 'POST'})
def contact ():

	if (request.method == 'POST'):
		# add entry to database
		name = request.form.get('name')
		email = request.form.get('email')
		phone = request.form.get('phone')
		message = request.form.get('message')
		
		entry = Contacts (name = name, email = email, phone_number = phone, date = datetime.now(), message = message)
		db.session.add (entry)
		db.session.commit ()

		'''mail.send_message ('new message from ' + name, 
							sender = email, 
							recipients = [params ['gmail_user']],
							body = message + 'new line' + phone
							)'''

	flash = ("Submission Swallowed. We'll get back to you when we want to XO", "success")
	return render_template ('contact.html', params = params)

app.run (debug = True)
