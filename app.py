#!/usr/bin/python

import os

from flask import Flask, render_template, request, redirect, url_for
from flask.ext.pymongo import PyMongo


app = Flask(__name__)
#app.config.from_envvar('APP_SETTINGS')
app.config['MONGO_URI'] = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/flask_test')
mongo = PyMongo(app)
 

#class User(mongo.db.Model):
#  id = mongo.db.Column(mongo.db.Integer, primary_key=True)
#  name = mongo.db.Column(mongo.db.String(100))
#  email = mongo.db.Column(mongo.db.String(100))
#  def __init__(self, name, email):
#    self.name = name
#    self.email = email

@app.route('/')
def index():
  return render_template('index.html')
#  return render_template('index.html', users = User.query.all())

@app.route('/user', methods=['POST'])
def user():
  if request.method == 'POST':
    u = User(request.form['name'], request.form['email'])
    mongo.db.session.add(u)
    mongo.db.session.commit()

  return redirect(url_for('index'))

if __name__ == '__main__':
#mongo.db.create_all()
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)
