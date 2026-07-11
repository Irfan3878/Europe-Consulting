# models/success_story.py
from extensions import db
from datetime import datetime

class SuccessStory(db.Model):
    __tablename__ = 'success_stories'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    client_name = db.Column(db.String(100), nullable=True) # İsim gizlemek isterlerse boş kalabilir
    created_at = db.Column(db.DateTime, default=datetime.utcnow)