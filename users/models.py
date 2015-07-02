# -*- coding: utf-8 -*-

import flask.ext.login as ext_login
from flask.ext.mongoengine import MongoEngine

db = MongoEngine()
def registrator(state):
	db.init_app(state.app)
	
class User(db.Document, ext_login.UserMixin):
	pre_invite = db.BooleanField(default=True)
	name = db.StringField(max_length=50)
	email = db.EmailField(required=True, unique=True)

	def __str__(self):
		return self.email
