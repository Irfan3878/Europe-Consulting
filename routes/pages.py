# routes/pages.py
from flask import Blueprint, render_template
from models.success_story import SuccessStory

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/')
def home():
    # Ana sayfada en yeni eklenen 3 başarı hikayesini listele
    stories = SuccessStory.query.order_by(SuccessStory.created_at.desc()).limit(3).all()
    return render_template('home.html', stories=stories)

@pages_bp.route('/service')
def service():
    # Hizmetlerimiz sayfası
    return render_template('service.html')

@pages_bp.route('/contact')
def contact():
    # İletişim sayfası
    return render_template('contact.html')