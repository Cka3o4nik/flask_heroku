#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

import flask
from flask import render_template, request, redirect, url_for, make_response
from flask.ext.babel import Babel
from flask_wtf.csrf import CsrfProtect
from pymongo import read_preferences

import users as u

#app = u.app
mongo_uri=os.environ.get('MONGODB_URI', 'mongodb://127.0.0.1/<db name>')
app = flask.Flask(__name__)
app.config.update({
	'SECRET_KEY': '',
	'BABEL_DEFAULT_LOCALE': 'en',
	'MONGODB_SETTINGS': {
		'host': mongo_uri,
		'read_preference': read_preferences.ReadPreference.PRIMARY
	}
})

csrf = CsrfProtect(app)
app.register_blueprint(u.users, url_prefix='/users')
babel = Babel(app)

#from jinja2 import Environment
#jinja_env = Environment(extensions=['jinja2.ext.i18n'])
#jinja_env.install_null_translations()

#translations = get_gettext_translations()
#env.install_gettext_translations(translations)

# Landing part

def get_common_context():
	return {} # , users=User.objects

@app.route('/subscribe', methods=['POST'])
def subscribe():
#	form = (request.form or None)
#	u.User(
#	form.populate_obj(user)
	username=request.form['name']
	email=request.form['email']
	try:
		u.User(name=username, email=email).save()
	except u.db.ValidationError:
		return u.render_template('subscribe.html', name=username, email=email, msg=u"Incorrect email")
	except u.db.NotUniqueError:
		return render_template('msg.html', msg=u"This email already registered!")
		
	return render_template('msg.html', msg=u'Thanks!') # , users=User.objects


@csrf.error_handler
def csrf_error(reason):
    return render_template('msg.html', msg=reason), 400

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.route('/landing')
def landing():
	return render_template('landing.html')

@app.route('/')
def index():
	return render_template('home.html')

# a route for generating sitemap.xml
@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
			from datetime import datetime, timedelta

			"""Generate sitemap.xml. Makes a list of urls and date modified."""
			pages=[]
			ten_days_ago=(datetime.now() - timedelta(days=10)).date().isoformat()
			# static pages
			for rule in app.url_map.iter_rules():
					if "GET" in rule.methods and len(rule.arguments)==0:
							pages.append(
													 [rule.rule,ten_days_ago]
													 )
			
			# user model pages
#			 users=User.query.order_by(User.modified_time).all()
#			 for user in users:
#					 url=url_for('user.pub',name=user.name)
#					 modified_time=user.modified_time.date().isoformat()
#					 pages.append([url,modified_time]) 

			sitemap_xml = render_template('sitemap_template.xml', url_root=request.url_root[:-1], pages=pages)
			response = make_response(sitemap_xml)
			response.headers["Content-Type"] = "application/xml"		
		
			return response

@app.route('/<file_name>.txt')
def send_text_file(file_name):
		"""Send your static text file."""
		file_dot_text = file_name + '.txt'
		return app.send_static_file(file_dot_text)

# Google verification file
#@app.route('/XXX.html')
#def send_google_file():
#		return app.send_static_file('XXX.html')

###
# The functions below should be applicable to all Flask apps.
###

domain=os.environ.get('DOMAIN', u'your-default-root-domain')
@app.before_request
def redirect_www():
		from urlparse import urlparse, urlunparse

		"""Redirect www requests to root"""
		urlparts = urlparse(request.url)
#		print 'urlparts:', urlparts
		if urlparts.netloc == 'www.'+domain:
				urlparts_list = list(urlparts)
				urlparts_list[1] = domain
#				print 'condition works'
				return redirect(urlunparse(urlparts_list), code=301)

@app.after_request
def add_header(response):
		"""
		Add headers to both force latest IE rendering engine or Chrome Frame,
		and also to cache the rendered page for 10 minutes.
		"""
		response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
		response.headers['Cache-Control'] = 'public, max-age=600'
		return response


if __name__ == '__main__':
	from flask.ext.script import Manager, Server

	manager = Manager(app)

# Turn on debugger by default and reloader
	port = int(os.environ.get('PORT', 5000))
	debug = port != 80 # Debug only if not running at 80 port
	manager.add_command("runserver", Server(
			use_debugger = debug,
			use_reloader = debug,
			host = '0.0.0.0')
	)

#	if debug:
#		u.User.drop_collection()

	app.run(host=os.environ.get('HOST', '127.0.0.1'), port=port, debug=debug)
