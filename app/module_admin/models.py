from app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.module_users.models import User

class Admin(db.Model):
    __tablename__ = 'admin'

    # User id
    id = db.Column(UUID(as_uuid=True), db.ForeignKey(User.id), primary_key=True, default=uuid.uuid4())

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return f'Admin({self.id})'

    # To DELETE a row from the table
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    # To SAVE a row from the table
    def save(self):
        db.session.add(self)
        db.session.commit()

    def toJSON(self):
        return { 'id': self.id }