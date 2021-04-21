from shortener import app, db
from flask import render_template, request, redirect
import string
import random

# change this base URL to your domain name after publishing
base_url = "https://shortener.vandit.cf/"


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        url_received = request.form["entered_url"]
        short = shorten_url()
        display_short = base_url + short
        database(url_received, short, display_short)
        docs = db.collection('urls').get()
        return render_template('index.html', short_url=display_short, docs=docs)
    else:
        docs = db.collection('urls').get()
        return render_template('index.html', short_url="", docs=docs)


@app.route("/<short>")
def redirecting(short):
    query = db.collection('urls').document(short).get()
    if query.exists:
        long = query.to_dict()['long_url']
        return redirect(long)
    else:
        return "<h1>URL Doesn't exists</h1>"


def shorten_url():
    letters = string.ascii_lowercase + string.ascii_uppercase
    while True:
        rand_letters = random.choices(letters, k=3)
        rand_letters = "".join(rand_letters)
        collection = db.collection('urls').where("short", "==", rand_letters).get()
        if not collection:
            return rand_letters


def database(url_received, short, display_short):
    data = {
        'long_url': url_received,
        'short': short,
        'short_url': display_short
    }
    db.collection('urls').document(short).set(data)
