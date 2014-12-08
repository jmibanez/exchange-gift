from flask import Blueprint, jsonify, render_template, flash, redirect, url_for, request, abort
from flask.ext.bootstrap import Bootstrap
from gifts2.admin.forms import RegistrationForm, UploadForm
from gifts2.models import Registration, WishList, UserMeta
from gifts2 import manager

from google.appengine.ext import ndb
from google.appengine.api import memcache, users
import datetime

admin = Blueprint('admin', __name__, template_folder='admin_templates')

@admin.route('/')
def admin_root():
    return render_template('index.html')

@admin.route('/run-matches')
def do_matching():
    year = str(datetime.date.today().year)

    manager.do_generate_matches(year)
    match_list = manager.get_match_list(year)

    return redirect(url_for('.list_matches'))

@admin.route('/matches')
def list_matches():
    year = str(datetime.date.today().year)
    match_list = manager.get_match_list(year)
    return render_template('match_list.html', match_list=match_list)
    

@admin.route('/send-email')
def send_matches():
    year = str(datetime.date.today().year)
    manager.do_send_match_emails(year)
    return render_template('match_email.html')


@admin.route('/metadata', methods=['GET'])
def start_upload_metadata():
    f = UploadForm()
    return render_template('upload.html', form=f,
                           target=url_for('.upload_metadata'))

@admin.route('/metadata', methods=['POST'])
def upload_metadata():
    f = UploadForm()
    meta_f = request.files[f.file_uploaded.name]

    # Read a line, split into tuples
    data = meta_f.getvalue()
    tuple_list = []
    for l in data.split('\n'):
        if l:
            t = tuple(l.split(':'))
            tuple_list.append(t)

    manager.save_user_metadata_from_list(tuple_list)
    return redirect(url_for('.admin_root'))

@admin.route('/upload')
def start_bulk_registration():
    f = UploadForm()
    return render_template('upload.html', form=f,
                           target=url_for('.do_bulk_registration'))

@admin.route('/upload', methods=['POST'])
def do_bulk_registration():
    f = UploadForm()
    bulk_f = request.files[f.file_uploaded.name]

    # Read a line, split into tuples
    data = bulk_f.getvalue()
    tuple_list = []
    for l in data.split('\n'):
        if l:
            t = tuple(l.split(':'))
            tuple_list.append(t)

    manager.bulk_register_users_from_list(tuple_list)
    return redirect(url_for('.admin_root'))
