from datetime import datetime

from . import db
from .util import security


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(2048))
    password = db.Column(db.String(2048))
    username = db.Column(db.String(2048))
    # Can be admin or member
    role = db.Column(db.String(64), default="member")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def save(self):
        self.updated_at = datetime.utcnow()
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    def dict(self):
        return dict(
            email=self.email,
            username=self.username,
            role=self.role,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
    
    def check_password(self, password: str):
        return security.check_pwd(password, self.password)
    
    @staticmethod
    def new(email: str, password: str, username: str):
        u = User(email=email, password=security.enc_pwd(password), username=username)
        u.save()
        return u
