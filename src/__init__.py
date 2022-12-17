from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

from flask_cors import CORS
from oauthlib.oauth2 import WebApplicationClient
from flask_login import LoginManager

app = Flask(__name__,
            static_url_path='/',
            static_folder='static/class-ui/',
            template_folder='web/templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = False
db = SQLAlchemy(app)

CORS(app, supports_credentials=True)

# Configuration
GOOGLE_CLIENT_ID = "971809948453-j5ubj7vbocmg4fquiki07bn3cjv35fo8.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)



