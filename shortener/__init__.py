from flask import Flask
from flask_wtf.csrf import CSRFProtect
import firebase_admin
import pyrebase
from firebase_admin import firestore, credentials
from shortener.config import SECRET_KEY, Config

# initializing pyrebase
firebase = pyrebase.initialize_app(Config)

# initializing firebase-admin
cred = credentials.Certificate("shortener/serviceAccountKey.json")
default_app = firebase_admin.initialize_app(cred)

db = firestore.client()
auth = firebase.auth()

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
csrf = CSRFProtect(app)    # CSRF token

from shortener import routes
