from google.appengine.ext import ndb
from google.appengine.api import users, mail, memcache
from google.appengine.api.app_identity import get_application_id

from gifts2.models import Registration, RegistrationMatches, UserMeta, WishList

import logging

import datetime
import random
import pickle

REGISTRATION_LIST_KEY = "registration_list(%s)"
REGISTRATION_MATCH_LIST_KEY = "matches(%s)"
METADATA_KEY = "meta(%s)"

MAIL_FROM_TEMPLATE = "%%s@%s.appspotmail.com" % get_application_id()

def get_registration(user):
    r_str = memcache.get("registration(%s)" % user)
    if r_str:
        return pickle.loads(r_str)

    year = str(datetime.date.today().year)
    q = Registration.query()
    q = q.filter(Registration.user==user)
    q = q.filter(Registration.year==year)

    r = q.fetch(2)
    if len(r) == 1:
        return r[0]
    elif len(r) == 0:
        return None
    else:
        raise "Invalid data store state"

def register_user(user, reg_form):
    do_register_user(user, reg_form.cleaned_data['codename'])

def do_register_user(user, codename):
    year = str(datetime.date.today().year)
    r = Registration(year=year,
                     user=user,
                     codename=codename)
    r.put()

    memcache.set("registration(%s)" % user, pickle.dumps(r), time=3600)

    # Delete cached registration list
    memcache.delete(REGISTRATION_LIST_KEY % year, 0)

def get_registration_list(year):
    # Check memcache for the registration list
    cached_reglist = memcache.get(REGISTRATION_LIST_KEY % year)
    reg_list = []
    if not cached_reglist:
        q = Registration.query()
        q = q.filter(Registration.year==year)

        # We'll stream off every registration for the year until end
        for reg in q:
            reg_list.append(reg)

        # Cache it
        memcache.set(REGISTRATION_LIST_KEY % year, pickle.dumps(reg_list), time=3600)
    else:
        # Load reg_list from the cached copy
        reg_list = pickle.loads(cached_reglist)

    return reg_list

def get_current_wishlist(reg):
    r_str = memcache.get("wishlist(%s)" % reg)
    if r_str:
        return pickle.loads(r_str)

    q = WishList.query()
    q = q.filter(WishList.registration==reg.key)
    q = q.order(-WishList.version)

    r = q.fetch(1)
    if len(r) == 1:
        return r[0]
    else:
        return None

def update_wishlist(reg, current_wishlist, f):
    new_version = 1
    new_text = f.cleaned_data['text']
    if current_wishlist:
        new_version = current_wishlist.version + 1

    if current_wishlist and new_text != current_wishlist.text:
        new_wishlist = WishList(text = new_text, version = new_version,
                                registration = reg)

        new_wishlist.put()
        memcache.set("wishlist(%s)" % reg, pickle.dumps(new_wishlist), time=3600)

def lookup_meta(user):
    meta_str = memcache.get(METADATA_KEY % user)
    if meta_str:
        return pickle.loads(meta_str)

    q = UserMeta.query()
    q = q.filter(UserMeta.user==user)

    r = q.fetch(2)
    if len(r) == 1:
        meta = r[0]
        memcache.set(METADATA_KEY % user, pickle.dumps(meta), time=3600)
        return meta
    else:
        return None

def bulk_register_users_from_list(user_list):
    for user_tuple in user_list:
        email = user_tuple[0]
        codename = user_tuple[1]
        user = users.User(email=email)
        do_register_user(user, codename)


def save_user_metadata(user, sex):
    q = UserMeta.query()
    q = q.filter(UserMeta.user==user)

    r = q.fetch(2)
    if len(r) == 0:
        meta = UserMeta(user = user, sex = sex)
        meta.put()
        memcache.set(METADATA_KEY % user, pickle.dumps(meta), time=3600)
    else:
        meta = r[0]
        meta.sex = sex
        meta.put()
        memcache.set(METADATA_KEY % user, pickle.dumps(meta), time=3600)

def save_user_metadata_from_list(metadata_list):
    for meta_tuple in metadata_list:
        user = meta_tuple[0]
        sex  = meta_tuple[1]
        save_user_metadata(users.User(user), sex)

def do_generate_matches(year):
    # Delete all existing matches first
    q = get_match_list(year)
    for match in q:
        match.key.delete()

    memcache.delete(REGISTRATION_MATCH_LIST_KEY % year, 0)

    reg_list = get_registration_list(year)

    # Randomly pick a person in the reg_list for a registration match

    # Initial giver
    start_giver = random.choice(reg_list)

    giver = start_giver
    taker = None
    while len(reg_list) != 1:
        # Initial taker
        taker = random.choice(reg_list)

        logging.info("Taker %s" % taker)

        # Spin if taker == giver
        while giver.user == taker.user:
            taker = random.choice(reg_list)

        __save_match(year, giver, taker)

        # Remove giver from list
        reg_list.remove(giver)

        # Taker is new giver
        giver = taker

    taker = reg_list[0]
    # The last taker is then assigned to start_giver
    __save_match(year, taker, start_giver)

    # Done!

def get_match_list(year):
    q = RegistrationMatches.query()
    q = q.filter(RegistrationMatches.year==year)

    return q

def do_send_match_email(item, reg, match_giver_givermap):
    email = item['email']
    giver_codename = item['giver_codename']
    taker_codename = item['taker_codename']
    taker_email    = item['taker_email']
    taker_sex      = item['taker_sex']
    taker_wish     = item['taker_wish']
    giver_giver_codename = match_giver_givermap[email]

    mail.send_mail(sender = MAIL_FROM_TEMPLATE % "matching-elves",
                   to = email,
                   subject = 'Exchange Gift Match!',
                   body = """
Dear '%s',

The exchange gift elves have finished sorting and making the lists!

Your exchange gift receipient is '%s' ('%s'), while '%s' has picked
you for their gift. Gifts should be worth at most PhP 300.00.

Merry Christmas!

--
The Exchange Gift Elves @ CodeFlux
""" % (giver_codename, taker_email, taker_codename, giver_giver_codename))

    reg.sent = True
    reg.put()

def do_send_match_emails(year):
    q = get_match_list(year)

    match_listmap = []
    match_giver_givermap = {}

    # Generate a match map first
    for reg_match in q:
        giver = reg_match.giver.get()
        receiver = reg_match.receiver.get()
        if not reg_match.sent:
            match_map = {}
            match_map['email'] = giver.user.email()
            match_map['giver_codename'] = giver.codename
            match_map['taker_codename'] = receiver.codename
            match_map['taker_email']    = receiver.user.email()
            wish = get_current_wishlist(receiver)
            if not wish:
                wish = "(Uhh, %s didn't make a wish. Hmm.)" % match_map['taker_codename']
            else:
                wish = wish.text
            match_map['taker_wish'] = wish
            receiver_meta = lookup_meta(receiver.user)
            if receiver_meta:
                match_map['taker_sex']  = receiver_meta.sex
            else:
                match_map['taker_sex']  = "gender undetermined"

            match_map['reg'] = reg_match

            match_listmap.append(match_map)

        match_giver_givermap[receiver.user.email()] = giver.codename

    # Once we generate the list to process, we send email
    for item in match_listmap:
        do_send_match_email(item, item['reg'], match_giver_givermap)

def __save_match(year, giver, taker):
    match = RegistrationMatches(giver = giver.key, receiver = taker.key, year = year)
    match.put()

