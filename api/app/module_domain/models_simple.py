# app/models.py

from app import db

class SocialMedia(db.Model):
    __tablename__ = 'SocialMedia'

    name = db.Column(db.String, primary_key=True)