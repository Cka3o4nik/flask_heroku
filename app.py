#!/usr/bin/python

import os

from flask import Flask, render_template, request, redirect, url_for
#from flask.ext.pymongo import PyMongo

from flask.ext.script import Manager, Server
from mongoengine import connect, Document, StringField
#from tumblelog import app


app = Flask(__name__)
#app.config.from_envvar('APP_SETTINGS')
#app.config['MONGO_URI'] = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/flask_test')
connect('flask_test')
 
class User(Document):
    email = StringField(required=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)

#class User(mongo.db.Model):
#	id = mongo.db.Column(mongo.db.Integer, primary_key=True)
#	name = mongo.db.Column(mongo.db.String(100))
#	email = mongo.db.Column(mongo.db.String(100))
#	def __init__(self, name, email):
#		self.name = name
#		self.email = email

@app.route('/')
def index():
  return render_template('base.html')

@app.route('/login')
def login():
  return render_template('index.html', users = User.objects)

@app.route('/user', methods=['POST'])
def user():
	if request.method == 'POST':
		u = User(request.form['name'], request.form['email'])
		mongo.db.session.add(u)
		mongo.db.session.commit()

	return redirect(url_for('index'))

@app.route('/ross')
def ross():
	ross = User(email='ross@example.com', first_name='Ross', last_name='Lawley').save()


if __name__ == '__main__':
#	mongo.db.create_all()
	manager = Manager(app)

# Turn on debugger by default and reloader
	manager.add_command("runserver", Server(
			use_debugger = True,
			use_reloader = True,
			host = '0.0.0.0')
	)

	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)
