from flask.ext.wtf import Form

from wtforms import widgets, BooleanField, TextField, DecimalField, HiddenField, IntegerField, SelectMultipleField, DateField, TextAreaField, DateTimeField, ValidationError, SelectField, FieldList, FileField, FloatField, Field
from wtforms.validators import Required, Optional

from wtforms.ext.appengine.ndb import model_form

from gifts2 import models

class RegistrationForm(Form):
    codename = TextField('Your "codename"', validators=[Required()])
    wishlist = TextAreaField('Your wishlist')

class UploadForm(Form):
    file_uploaded = FileField('File')

