# models/user.py
from extensions import db, bcrypt
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # Rol Tabanlı Erişim Kontrolü (RBAC) için: 'user' veya 'admin'
    role = db.Column(db.String(20), default='user', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişki: Bir kullanıcının birden fazla randevusu olabilir
    appointments = db.relationship('Appointment', backref='client', lazy=True)

    # Şifreyi güvenli bir şekilde Bcrypt ile hash'leme fonksiyonu
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # Giriş yapılırken girilen şifrenin doğruluğunu kontrol eden fonksiyon
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)