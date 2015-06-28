#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

import flask
from flask import current_app, Blueprint, render_template, request, redirect, url_for

from flask_wtf import Form
from wtforms import BooleanField, TextField, PasswordField, validators
from wtforms.csrf.session import SessionCSRF
import flask.ext.login as ext_login
from flask.ext.login import login_required, current_user
from flask.ext.mongoengine import MongoEngine

users = Blueprint('users', __name__, template_folder='templates')

login_manager = ext_login.LoginManager()
db = MongoEngine()

def registrator(state):
	app = state.app
	db.init_app(app)
	login_manager.init_app(app)
	
users.record(registrator)

class User(db.Document, ext_login.UserMixin):#
	pre_invite = db.BooleanField(default=True)
	name = db.StringField(max_length=50)
	email = db.EmailField(required=True, unique=True)

class LoginForm(Form):
#	username = TextField('Username', [validators.Length(min=4, max=25)])
	email = TextField('Email', [validators.Required(), validators.Length(min=6, max=35)])
	password = PasswordField('Password', [ validators.Required() ])

	def get_user(self):
			print self.email.data
			return User.objects.get_or_404(email=self.email.data)#.first()
			return User.objects.first_or_404(email=self.email.data)


class RegistrationForm(LoginForm):
	username = TextField('Username', [validators.Length(min=4, max=25)])
#	email = TextField('Email Address', [validators.Length(min=6, max=35)])
	password = PasswordField('New Password', [
			validators.Required(),
			validators.EqualTo('confirm', message='Passwords must match')
	])
	confirm = PasswordField('Repeat Password')
	accept_tos = BooleanField('I accept the TOS', [validators.Required()])

# User authentication

@login_manager.user_loader
def load_user(userid):
	return User.objects.get(id=userid)


@users.route("/logout")
@login_required
def logout():
		ext_login.logout_user()
		return redirect(url_for('index'))


@users.route('/profile', methods=['GET'])
def profile():
#	import pdb
#	pdb.set_trace()
	return flask.render_template('msg.html', msg=u"%s's profile!"%getattr(current_user, 'email', 'Anonymous'))

def next_is_valid(next):
	return current_app.debug

@users.route('/login', methods=['GET', 'POST'])
def login():
		# Here we use a class of some kind to represent and validate our
		# client-side form data. For example, WTForms is a library that will
		# handle this for us.
		print 'Begin login procedure'
		form = LoginForm()
		if form.validate_on_submit():
				user = form.get_user()
				print 'Login and validate the user'
				ext_login.login_user(user)

				print 'Logged in successfully.'
				flask.flash('Logged in successfully.')

				next = flask.request.args.get('next')
				if not next_is_valid(next):
						return flask.abort(400)

				return flask.redirect(next or url_for('users.profile'))
		else:
			print 'Login errors:'
			for field, err_list in form.errors.items():
				print field, ':', err_list[0]

		print 'render_template form.html'
		return flask.render_template('form.html', form=form)


@users.route('/register', methods=['GET', 'POST'])
def register():
		form = RegistrationForm()
		if form.validate_on_submit():
				user = User(pre_invite=False)
				form.populate_obj(user)
				user.save()
				print 'User saved!'
				flask.flash('Thanks for registering')

				ext_login.login_user(user)
				return redirect(url_for('users.profile'))
#				 return redirect(url_for('login'))
		else:
			for field, err_list in form.errors.items():
				print field, ':', err_list[0]

		return render_template('form.html', form=form)


if __name__ == '__main__':
	pass
