# app.py
import os
from flask import Flask
from extensions import db, bcrypt, login_manager, csrf, mail
from dotenv import load_dotenv

# .env dosyasındaki verileri yükle (Diğer ayarlar için aktif kalabilir)
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # ---- GÜVENLİK VE ALTYAPI YAPILANDIRMASI ----
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'varsayilan-guvenli-anahtar-123')
    
    instance_path = os.path.join(app.root_path, 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(instance_path, 'database.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
    
    # ---- FLASK-MAIL (E-POSTA SUNUCUSU) YAPILANDIRMASI ----
    # .env çakışmalarını önlemek ve BadCredentials hatasını çözmek için doğrudan tanımlıyoruz:
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'setiarif38@gmail.com'
    
    # 🚨 DIKKAT: Google'dan aldığın 16 haneli uygulama şifresini 
    # aralarındaki boşlukları tamamen SİLEREK alttaki tırnak içine yapıştır kanka!
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    
    app.config['MAIL_DEFAULT_SENDER'] = 'setiarif38@gmail.com'
    
    # ---- UZANTILARI UYGULAMAYA BAĞLAMA ----
    db.init_app(app)
    mail.init_app(app) 
    bcrypt.init_app(app)
    csrf.init_app(app) 
    
    # Oturum Yönetimi Ayarları
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Bu sayfaya erişmek için lütfen giriş yapın.'
    login_manager.login_message_category = 'warning'
    
    # ---- BLUEPRINT'LERİ (ROTALARI) KAYDETME ----
    from routes.pages import pages_bp
    from routes.auth import auth_bp
    from routes.appointments import appointments_bp
    from routes.admin import admin_bp
    
    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(appointments_bp, url_prefix='/appointments')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    with app.app_context():
        db.create_all()
        
    return app

if __name__ == '__main__':
    app = create_app()
    is_debug = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    app.run(debug=is_debug)