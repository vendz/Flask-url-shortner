from shortener import app, db, auth
from flask import render_template, request, redirect, session, url_for, flash, g, send_from_directory
from shortener.forms import RegisterForm, LoginForm
from datetime import timedelta
import string
import random
import inspect
import os

# change this base URL to your domain name after publishing
base_url = "http://127.0.0.1:5000/"


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsof.icon')


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        url_received = request.form["entered_url"]
        short = shorten_url()
        display_short = base_url + short
        database(url_received, short, display_short)
        docs = db.collection('urls').get()
        return render_template('index.html', short_url=display_short, docs=docs)
    elif request.method == 'GET':
        if g.user is not None:
            return redirect(url_for('account_page', user=session['email']))
        else:
            docs = db.collection('urls').get()
            return render_template('index.html', short_url="", docs=docs)


@app.route("/<short>")
def redirecting(short):
    query = db.collection('all_urls').document(short).get()
    if query.exists:
        long = query.to_dict()['long_url']
        return redirect(long)
    else:
        return render_template('page_not_found.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if g.user is not None:
            return redirect(url_for('account_page', user=session['email']))
    form1 = LoginForm()
    session.pop('logged_in', None)
    if form1.validate_on_submit():
        user = auth.sign_in_with_email_and_password(form1.email.data, form1.password.data)
        user = auth.refresh(user['refreshToken'])
        data = auth.get_account_info(user['idToken'])  # get user information
        email_verified = data['users'][0]['emailVerified']
        session['token'] = user['idToken']
        email_address = db.collection('users').document(form1.email.data).get()
        if email_address.exists:
            email_data = email_address.to_dict()['email_address']
            session['email'] = email_data
        if email_verified:
            session['logged_in'] = True
            return redirect(url_for('account_page', user=session['email']))
        else:
            return redirect(url_for('email_verification'))

    if form1.errors != {}:  # if no errors occur from validators
        for err_msg in form1.errors.values():
            flash(err_msg, category='danger')
    return render_template('login.html', form=form1)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        if g.user is not None:
            return redirect(url_for('account_page', user=session['email']))
    form2 = RegisterForm()
    session.pop('logged_in', None)
    if form2.validate_on_submit():
        signin = auth.create_user_with_email_and_password(form2.email_address.data, form2.password.data)
        auth.send_email_verification(signin['idToken'])  # for email verification
        session['token'] = signin['idToken']
        session['email'] = form2.email_address.data

        user_database(email_address=form2.email_address.data)

        return redirect(url_for('is_email_verified'))
    if form2.errors != {}:  # if no errors occur from validators
        for err_msg in form2.errors.values():
            flash(err_msg, category='danger')
    return render_template('register.html', form=form2)


@app.route('/verify_email')
def is_email_verified():
    try:
        data = auth.get_account_info(session['token'])  # get user information
        email_verified = data['users'][0]['emailVerified']
    except Exception as e:
        print(e)
        return redirect(url_for('index'))
    if email_verified:
        session['logged_in'] = True
        return redirect(url_for('account_page', user=session['email']))
    else:
        return render_template('email_verification.html')


@app.route('/account', methods=["GET", "POST"])
def account_page():
    if g.user is not None:
        if request.method == "POST":
            url_received = request.form["entered_url"]
            short = shorten_url()
            display_short = base_url + short
            database(url_received, short, display_short)
            docs = db.collection('users').document(session['email']).collection('urls').get()
            return render_template('account.html', short_url=display_short, docs=docs)
        else:
            docs = db.collection('users').document(session['email']).collection('urls').get()
            return render_template('account.html', user="", docs=docs, shorten_url="")
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    if g.user is not None:
        session.pop('logged_in', None)
        session.pop('token', None)
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=300)
    g.user = None
    if 'logged_in' in session:
        g.user = session['logged_in']


def shorten_url():
    letters = string.ascii_lowercase + string.ascii_uppercase
    while True:
        rand_char = "".join(random.choices(letters + string.digits, k=3))
        collection = db.collection('all_urls').where("short", "==", rand_char).get()
        if not collection:
            return rand_char


def database(url_received, short, display_short):
    data = {
        'long_url': url_received,
        'short': short,
        'short_url': display_short
    }
    daddy = whosdaddy()
    if daddy == 'account_page':
        db.collection('all_urls').document(short).set(data)
        db.collection('users').document(session['email']).collection('urls').document().set(data)
    else:
        db.collection('urls').document(short).set(data)
        db.collection('all_urls').document(short).set(data)


def user_database(email_address):
    data = {
        'email_address': email_address
    }
    db.collection('users').document(email_address).set(data)


def whosdaddy():
    return inspect.stack()[2][3]
