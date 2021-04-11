from shortener import app, db
from flask import render_template, request, redirect
import string
import random

# change this base URL to your domain name after publishing
base_url = "http://127.0.0.1:5000/"


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        url_received = request.form["entered_url"]
        url_check = db.collection('urls').where("long_url", "==", url_received).get()   # check if url already exists
        for url in url_check:
            exist_url = url.to_dict()
            res = bool(exist_url)
            if res:
                return render_template('index.html', short_url=exist_url['short_url'])
            else:
                short = shorten_url()
                display_short = base_url + short
                data = {
                    'long_url': url_received,
                    'short': short,
                    'short_url': display_short
                }
                db.collection('urls').document(short).set(data)
                if short is not None:
                    return render_template('index.html', short_url=display_short)
    else:
        return render_template('index.html', short_url="")


@app.route("/<short>")
def redirecting(short):
    query = db.collection('urls').document(short).get()
    if query.exists:
        long = query.to_dict()['long_url']
        return redirect(long)
    else:
        return "<h1>URL Doesn't exists</h1>"


@app.route('/all-urls')
def display_all():
    docs = db.collection('urls').get()
    for doc in docs:
        print(doc.to_dict())
        arr = []
    return "hello"


def shorten_url():
    letters = string.ascii_lowercase + string.ascii_uppercase
    while True:
        rand_letters = random.choices(letters, k=3)
        rand_letters = "".join(rand_letters)
        collection = db.collection('urls').where("short", "==", rand_letters).get()
        if not collection:
            return rand_letters
