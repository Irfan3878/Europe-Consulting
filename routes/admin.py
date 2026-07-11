# routes/admin.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.appointment import Appointment
from models.success_story import SuccessStory
from functools import wraps
from models.user import User
admin_bp = Blueprint('admin', __name__)

# 🔒 GÜVENLİK KALKANI: Yetkisiz Giriş Engelleme (Broken Access Control Koruması)
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Kullanıcı giriş yapmamışsa veya rolü admin değilse içeri alma
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Bu sayfaya erişim yetkiniz bulunmamaktadır!', 'danger')
            return redirect(url_for('pages.home'))
        return f(*args, **kwargs)
    return decorated_function

# Admin Yönetim Paneli Ana Sayfası
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Tüm randevuları ve başarı hikayelerini çekip panele gönderiyoruz
    all_appointments = Appointment.query.order_by(Appointment.created_at.desc()).all()
    all_stories = SuccessStory.query.order_by(SuccessStory.created_at.desc()).all()
    return render_template('admin/dashboard.html', appointments=all_appointments, stories=all_stories)

# Randevu Durumu Güncelleme (Onaylama / Reddetme)
@admin_bp.route('/appointment/update/<int:id>/<string:status>')
@login_required
@admin_required
def update_appointment(id, status):
    if status not in ['approved', 'rejected']:
        flash('Geçersiz işlem işlemi.', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    appointment = Appointment.query.get_or_404(id)
    appointment.status = status
    db.session.commit()
    
    flash(f'Randevu durumu başarıyla "{status}" olarak güncellendi.', 'success')
    return redirect(url_for('admin.dashboard'))

# Yeni Başarı Hikayesi Ekleme Rotası
@admin_bp.route('/story/add', methods=['POST'])
@login_required
@admin_required
def add_story():
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    client_name = request.form.get('client_name', '').strip()

    if not title or not content:
        flash('Başlık ve içerik alanları boş bırakılamaz.', 'danger')
        return redirect(url_for('admin.dashboard'))

    new_story = SuccessStory(
        title=title,
        content=content,
        client_name=client_name if client_name else "Anonim Müşteri"
    )
    
    db.session.add(new_story)
    db.session.commit()
    
    flash('Yeni başarı hikayesi web sitesinde yayınlanmak üzere eklendi!', 'success')
    return redirect(url_for('admin.dashboard'))
# Kayıtlı Kullanıcıları Listeleme (Sadece Admin Görebilir)
@admin_bp.route('/users')
@login_required
@admin_required
def user_list():
    # Şifre hash'i asla template'e gönderilmiyor, sadece güvenli alanlar çekiliyor
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)