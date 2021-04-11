from flask import Flask
from flask_wtf.csrf import CSRFProtect
import firebase_admin
from firebase_admin import firestore, credentials

# initializing firebase-admin
cred = credentials.Certificate("shortener/serviceAccountKey.json")
default_app = firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)
app.config['SECRET_KEY'] = "c6e803cd18a8c528c161eb9fcf013245248506ffb540ff70"
csrf = CSRFProtect(app)    # CSRF token

from shortener import routes
