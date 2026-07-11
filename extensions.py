# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect

# Araçların ilk tanımlamaları (Boş nesneler olarak)
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
csrf = CSRFProtect()

# Kullanıcı oturum yükleyicisi (Giriş yapan kullanıcıyı ID'sinden tanır)
@login_manager.user_loader
def load_user(user_id):
    from models.user import User
    return User.query.get(int(user_id))
# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail  # <-- Bunu ekle

db = SQLAlchemy()
csrf = CSRFProtect()
mail = Mail()  # <-- Bunu tanımla
