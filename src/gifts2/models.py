from google.appengine.ext import ndb

class Registration(ndb.Model):
    year = ndb.StringProperty()
    user = ndb.UserProperty()
    codename = ndb.StringProperty()

class WishList(ndb.Model):
    text = ndb.StringProperty()
    registration = ndb.KeyProperty(kind=Registration)
    version = ndb.IntegerProperty()

    def to_form(self, form_class):
        form_data = {}
        form_data['text'] = self.text
        return form_class(form_data)

class RegistrationMatches(ndb.Model):
    giver = ndb.KeyProperty(kind=Registration)
    receiver = ndb.KeyProperty(kind=Registration)
    year = ndb.StringProperty()
    sent = ndb.BooleanProperty(required = False)


class UserMeta(ndb.Model):
    user = ndb.UserProperty()
    sex = ndb.StringProperty(choices = ( 'M', 'F' ))
