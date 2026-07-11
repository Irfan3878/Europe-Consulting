# routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models.user import User
import re

# Blueprint tanımı
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Kullanıcı zaten giriş yapmışsa ana sayfaya postala
    if current_user.is_authenticated:
        return redirect(url_for('pages.home'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # 🔒 GÜVENLİK: Boş alan kontrolü
        if not username or not email or not password:
            flash('Lütfen tüm alanları doldurun.', 'danger')
            return render_template('register.html')
            
        # 🔒 GÜVENLİK: E-posta format doğrulaması (Regex)
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Geçersiz e-posta adresi formatı.', 'danger')
            return render_template('register.html')
        
        # Kullanıcı adı veya e-posta adresi daha önce alınmış mı?
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('Bu kullanıcı adı veya e-posta zaten kullanımda.', 'danger')
            return render_template('register.html')
        
        # Yeni kullanıcı nesnesi oluşturma (Şifre set_password içinde hash'leniyor)
        new_user = User(username=username, email=email, role='user')
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Kayıt başarıyla tamamlandı! Şimdi giriş yapabilirsiniz.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('pages.home'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        
        # 🔒 GÜVENLİK: Jenerik hata mesajı (Saldırganın kullanıcı tespiti yapmasını engeller)
        if user and user.check_password(password):
            login_user(user)
            flash('Başarıyla giriş yapıldı, hoş geldiniz!', 'success')
            
            # Eğer giriş yapan kişi admin ise direkt admin paneline yönlendir
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('pages.home'))
        else:
            flash('E-posta adresi veya şifre hatalı.', 'danger')
            
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required # 🔒 GÜVENLİK: Giriş yapmayan biri bu rotayı tetikleyemez
def logout():
    logout_user()
    flash('Başarıyla çıkış yapıldı.', 'info')
    return redirect(url_for('pages.home'))