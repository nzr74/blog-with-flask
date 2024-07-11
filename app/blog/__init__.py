from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from faker import Faker

app = Flask(__name__)
app.config["SECRET_KEY"] = (
    "36d80644abb4e0bee5fde655a15f6e792b55db967076c6a7eee50682495d47d5"
)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "please login"
login_manager.login_message_category = "info"
fake = Faker()

from blog import routes
