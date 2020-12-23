from datetime import datetime

from . import db
from .util import security, files


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(2048))
    password = db.Column(db.String(2048))
    username = db.Column(db.String(2048))
    # Can be admin or member
    role = db.Column(db.String(64), default="member")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship("Post", backref="user")
    reviews = db.relationship("Review", backref="user")
    suggestions = db.relationship("Suggestion", backref="user")
    code = db.relationship("Code", backref="user")

    def save(self):
        self.updated_at = datetime.utcnow()
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    def dict(self):
        return dict(
            id=self.id,
            email=self.email,
            username=self.username,
            role=self.role,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
    
    def check_password(self, password: str):
        return security.check_pwd(password, self.password)

    def set_password(self, password: str):
        self.password = security.enc_pwd(password)
        self.save()
    
    @staticmethod
    def new(email: str, password: str, username: str):
        u = User(email=email, password=security.enc_pwd(password), username=username)
        u.save()
        return u


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(2048))
    description = db.Column(db.Text)
    public = db.Column(db.Boolean, default=True)
    suggestions_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    code = db.relationship("Code", backref="post")
    reviews = db.relationship("Review", backref="post")
    suggestions = db.relationship("Suggestion", backref="post")

    def save(self):
        self.updated_at = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def dict(self):
        return dict(id=self.id, title=self.title, description=self.description, public=self.public,
                    user=self.user.dict(), suggestions_enabled=self.suggestions_enabled, created_at=self.created_at,
                    updated_at=self.updated_at, code=[c.dict() for c in self.code])


class Code(db.Model):
    __tablename__ = "code"
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(64))
    language = db.Column(db.String(128), default="plaintext")
    path = db.Column(db.String(1024))
    # If the code file was hosted locally or not
    local = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    suggestions = db.relationship("Suggestion", backref="code")

    def save(self):
        self.updated_at = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get_content(self):
        return files.get_encrypted_file_contents(self.filename, local=self.local, username=self.user.username)

    def dict(self):
        d = dict(id=self.id, local=self.local, path=self.path, language=self.language, created_at=self.created_at,
                 filename=self.filename, updated_at=self.updated_at, user=self.user.dict())
        return d


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    content = db.Column(db.Text)
    stars = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))

    def save(self):
        self.updated_at = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def dict(self):
        return dict(id=self.id, title=self.title, content=self.content, stars=self.stars,
                    user=self.user.dict(), created_at=self.created_at, updated_at=self.updated_at)


class Suggestion(db.Model):
    __tablename__ = "suggestions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    code_id = db.Column(db.Integer, db.ForeignKey("code.id"))

    def save(self):
        self.updated_at = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def dict(self):
        return dict(id=self.id, title=self.title, content=self.content,
                    created_at=self.created_at, updated_at=self.updated_at,
                    code=self.code.dict(), user=self.user.dict())
