# Exchange Gift

## Bootstrap Development Environment

NB: It is recommended that you run this inside a virtualenv. To set up
virtualenv, please refer below.

Requirements:

 * Python 2.7

To set up, run:

    $ python2.7 ./bootstrap.py
    $ ./bin/buildout
    
This will install Buildout, pull dependencies (including the needed
Python AppEngine SDK), and set up needed symlinks for running
a development environment.


## Running the dev app server

To run the dev app server instance, after running buildout:

    $ ./bin/dev_appserver src
    

## Project Dependencies

* Flask
* AppEngine


## Setting up a Python virtualenv

Ensure your Python installation has `virtualenv` and `pip`. If you
don't have either, or are unsure, run the following commands:

    $ easy_install pip
    $ pip install virtualenv

Once installed, run `virtualenv` to help isolate project dependencies:

    $ virtualenv env

Make sure to activate the `virtualenv` in your shell when working on
the app:

    $ source env/bin/activate
