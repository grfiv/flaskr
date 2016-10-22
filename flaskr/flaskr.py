# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash


# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
# if environment variable 'FLASKR_SETTINGS' exists override the previous app.config.update
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


# end of Step 2: Application Setup Code

def init_db():
    """Initializes the database.

    Reads the schema.sql file we created
    and creates an empty sqlite database flaskr.db"""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables.

    Invoked on the CLI by 'flask initdb'
    which creates the sqlite database 'flaskr.db'"""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

# end of Step 4: Creating The Database


@app.route('/')
def show_entries():
    """
    This view shows all the entries stored in the database.

    It listens on the root of the application and will select title and text from the database.
    The one with the highest id (the newest entry) will be on top.
    The rows returned from the cursor look a bit like dictionaries because we are using the sqlite3.Row row factory.

    The view function will pass the entries to the show_entries.html template

    :return: the rendered template
    """
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    """
    This view lets the user add new entries if they are logged in.

    This only responds to POST requests; the actual form is shown on the show_entries page.
    If everything worked we will flash() an information message to the next request and
    redirect back to the show_entries page

    Note that we check that the user is logged in
     (1) the logged_in key is present in the session
     (2) and True

    :return: redirect back to the show_entries page
    """
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
               [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

# end of Step 5: The View Functions

if __name__ == '__main__':
    app.run(host = '0.0.0.0')


