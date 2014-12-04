from flask import Blueprint, jsonify, render_template, flash, redirect, url_for, request, abort
from flask.ext.bootstrap import Bootstrap
from gifts2.admin.forms import RegistrationForm
from gifts2.models import Registration, WishList, UserMeta
from gifts2 import manager

from google.appengine.ext import ndb
from google.appengine.api import memcache, users
import datetime

web = Blueprint('web', __name__, template_folder='web_templates')


@web.route('/')
def web_root():
    u = users.get_current_user()
    reg = manager.get_registration(u)

    if reg:
        return redirect(url_for('.done_registering'))

    f = RegistrationForm()
    return render_template('registration.html', user=u, form=f)

@web.route('/register', methods=['POST'])
def do_register():
    u = users.get_current_user()
    reg = manager.get_registration(u)

    f = RegistrationForm()

    if reg == None:
        reg = Registration(user=u)

    if f.validate_on_submit():
        f.populate_obj(reg)
        reg.put()
        return redirect(url_for('.done_registering'))
    else:
        return render_template('registration.html', user=u, form=f)

@web.route('/thanks', methods=['GET', 'POST'])
def done_registering():
    return render_template('thanks.html')
