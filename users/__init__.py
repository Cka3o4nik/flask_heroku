#!/usr/bin/python
# -*- coding: utf-8 -*-

import flask
from flask import current_app, render_template, request, redirect, url_for

from flask_wtf import Form
from wtforms import BooleanField, TextField, PasswordField, validators
import flask.ext.login as ext_login
from flask.ext.login import login_required, current_user
from flask.ext.babel import lazy_gettext

import models as m

_ = lazy_gettext
login_manager = ext_login.LoginManager()

def registrator(state):
	m.registrator(state)
	login_manager.init_app(state.app)
	
users = flask.Blueprint('users', __name__, template_folder='templates')
users.record(registrator)

#class User(db.Document, ext_login.UserMixin):#
class LoginForm(Form):
#	username = TextField('Username', [validators.Length(min=4, max=25)])
	email = TextField('Email', [validators.Required(), validators.Length(min=6, max=35)])
	password = PasswordField(_('Password'), [ validators.Required() ])

	def get_user(self):
#			print self.email.data
			return m.User.objects.get_or_404(email=self.email.data)#.first()


class RegistrationForm(LoginForm):
	username = TextField(_('Username'), [validators.Length(min=4, max=25)])
	password = PasswordField(_('Password'), [
			validators.Required(),
			validators.EqualTo('confirm', message='Passwords must match')
	])
	confirm = PasswordField(_('Repeat Password'))
	accept_tos = BooleanField(_('I accept the TOS'), [validators.Required()])

#@login_required
#@users.route('/list')
#def user_list():
#	return render_template('msg.html' , msg='<br>'.join(['%s %s '%(u.name, u.email) for u in m.User.objects]))


# User authentication

@login_manager.user_loader
def load_user(userid):
#	print '!!!!!!!!!!!!!!!!! load_user CALL !!!!!!!!!!!!!!!!!'
	return m.User.objects.get(id=userid)
# load_user('558b33dd997a7c7701f2810a')

@users.route("/logout")
@login_required
def logout():
		ext_login.logout_user()
		return redirect(url_for('index'))


@users.route('/profile', methods=['GET'])
@login_required
def profile():
#	import pdb
#	pdb.set_trace()
	return flask.render_template('msg.html', msg=u'Профиль %s'%current_user.email)

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

				return flask.redirect(next or url_for('dashboard'))
		else:
			print 'Login errors:'
			for field, err_list in form.errors.items():
				print field, ':', err_list[0]
#			import pdb
#			pdb.set_trace()

		print 'render_template form.html'
		return flask.render_template('form.html', form=form, title=_(u'Log in'))


@users.route('/register', methods=['GET', 'POST'])
def register():
#		form = RegistrationForm(request.form or None)
		form = RegistrationForm()
		if form.validate_on_submit():
				user = User(pre_invite=False)
				form.populate_obj(user)
#				 user = User(form.username.data, form.email.data,
#										form.password.data)
				user.save()
				print 'User saved!'
				flask.flash('Thanks for registering')

				ext_login.login_user(user)
				return redirect(url_for('users.profile'))
#				 return redirect(url_for('login'))
		else:
			for field, err_list in form.errors.items():
				print field, ':', err_list[0]

		return render_template('form.html', form=form, title=_(u'Sign up'))


if __name__ == '__main__':
	pass
