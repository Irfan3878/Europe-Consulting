import os
from datetime import datetime
from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_mail import Message
from flask_login import current_user, login_required
from extensions import db, mail
from models.appointment import Appointment

appointments_bp = Blueprint('appointments', __name__)

# 💡 KRİTİK AYAR: Eğer .env dosyan okunamazsa sistemin hata vermemesi için
# alttaki tırnak içine projen için kullandığın GERÇEK GMAİL ADRESİNİ yaz kanka.
YEDEK_GONDERICI_MAIL = 'setiarif38@gmail.com'


@appointments_bp.route('/create', methods=['POST'])
def create():
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    phone = request.form.get('phone')
    service_type = request.form.get('service_type')
    appointment_date_raw = request.form.get('appointment_date')
    message_text = request.form.get('message')

    # 🔒 Basit doğrulama: zorunlu alanlar boş mu?
    if not all([fullname, email, phone, service_type, appointment_date_raw]):
        flash("Lütfen tüm zorunlu alanları doldurun.", "danger")
        return redirect(url_for('pages.home'))

    # Form'dan gelen string tarihi datetime objesine çeviriyoruz
    # HTML input tipine göre birkaç farklı format deneniyor
    parsed_date = None
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            parsed_date = datetime.strptime(appointment_date_raw, fmt)
            break
        except ValueError:
            continue

    if parsed_date is None:
        flash("Randevu tarihi formatı geçersiz.", "danger")
        return redirect(url_for('pages.home'))

    # 1. VERİ TABANINA KAYDETME İŞLEMİ
    new_app = Appointment(
        fullname=fullname,
        email=email,
        phone=phone,
        service_type=service_type,
        appointment_date=parsed_date,
        message=message_text,
        status='pending',
        user_id=current_user.id if current_user.is_authenticated else None
    )
    db.session.add(new_app)
    db.session.commit()

    aktif_gonderici = os.getenv('MAIL_USERNAME') or YEDEK_GONDERICI_MAIL

    # 2. OTOMATİK E-POSTA MOTORU
    try:
        # 🛡️ A - MÜŞTERİYE GİDEN PREMİUM ONAY MAİLİ
        user_msg = Message(
            subject="Randevu Başvurunuz Alındı | Europe Consulting",
            recipients=[email],
            sender=aktif_gonderici
        )
        user_msg.body = f"""Sayın {fullname},

Europe Consulting vize ve göçmenlik ofisine yaptığınız ön değerlendirme başvurusu başarıyla sistemimize ulaşmıştır.

Randevu ve Süreç Detayları:
-------------------------------------------
Talep Edilen Hizmet : {service_type}
Tercih Edilen Zaman : {appointment_date_raw}
İletişim Numaranız  : {phone}
-------------------------------------------

Evraklarınız ve siber güvenlik altyapımızla korunan verileriniz uzmanlarımız tarafından incelemeye alınmıştır. 24 saat içerisinde süreç danışmanınız sizinle bu mail adresi üzerinden iletişime geçecektir.

Bizlere güvendiğiniz için teşekkür ederiz.

Saygılarımızla,
Europe Consulting Operasyon Ekibi
"""
        mail.send(user_msg)

        # 🛡️ B - ADMİNE GİDEN ANLIK BİLDİRİM MAİLİ
        admin_recipient = os.getenv('ADMIN_EMAIL', 'admin@europeconsulting.com')
        admin_msg = Message(
            subject=f"🚨 YENİ BAŞVURU: {fullname} - {service_type}",
            recipients=[admin_recipient],
            sender=aktif_gonderici
        )
        admin_msg.body = f"""Sistem Yöneticisinin Dikkatine,

Web sitesi üzerinden yeni bir kurumsal randevu başvurusu oluşturuldu. Detaylar aşağıdadır:

Müşteri Bilgileri:
- Ad Soyad: {fullname}
- E-Posta: {email}
- Telefon: {phone}

Talep Detayları:
- Hizmet Alanı: {service_type}
- Planlanan Tarih: {appointment_date_raw}
- Kullanıcı Notu: {message_text}

Lütfen en kısa sürede admin paneline giriş yaparak ilgili adaya geri dönüş sağlayınız.
"""
        mail.send(admin_msg)

    except Exception as e:
        # SMTP veya Gönderici hatası olursa sitenin çökmesini engellemek için yakalıyoruz
        print(f"Siber Posta Motoru Hatası: {e}")
        flash("Randevunuz alındı ancak mail gönderiminde teknik bir aksaklık yaşandı.", "warning")
        return redirect(url_for('pages.home'))

    # Her şey sorunsuz bittiyse yeşil bildirim çakıyoruz
    flash("Randevunuz başarıyla oluşturuldu! Hem size hem ekibimize onay mailleri gönderildi.", "success")
    return redirect(url_for('pages.home'))


# 🛠️ PREMİUM RANDEVU PANELİ ROTASI
@appointments_bp.route('/my-appointments')
@login_required
def my_appointments():
    user_appointments = Appointment.query.filter_by(
        user_id=current_user.id
    ).order_by(Appointment.created_at.desc()).all()
    return render_template('my_appointments.html', appointments=user_appointments)