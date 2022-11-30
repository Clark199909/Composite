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
db = SQLAlchemy(app)

CORS(app)

# Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
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
