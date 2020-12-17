from os import getenv as env

# SQLALCHEMY
SQLALCHEMY_DATABASE_URI = env("SQLALCHEMY_DATABASE_URI", "sqlite:///../db.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False

# JWT
JWT_SECRET_KEY = env("JWT_SECRET_KEY", "in-development-so-no-need-to-hide-this-super-secret-key-right?")
JWT_ERROR_MESSAGE_KEY = "message"
JWT_ACCESS_TOKEN_EXPIRES = 86400
