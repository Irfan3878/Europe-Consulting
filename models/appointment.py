# models/appointment.py
from extensions import db
from datetime import datetime

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    # İlişkili kullanıcı ID'si (Ziyaretçi randevuları için nullable=True bırakıyoruz)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False) # Randevu günü ve saati
    service_type = db.Column(db.String(100), nullable=False) # Danışmanlık türü (Vize, Oturum vb.)
    message = db.Column(db.Text, nullable=True)
    
    # Randevu durumu kontrolü: 'pending' (beklemede), 'approved' (onaylandı), 'rejected' (iptal)
    status = db.Column(db.String(20), default='pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)