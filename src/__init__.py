from flask import Flask, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from os import path

db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile(path.join(path.dirname(path.abspath(__file__)), "config.py"))
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    Migrate(app, db)

    with app.app_context():
        # Import routes
        from .routes import auth, posts, code, reviews

        # Import errors
        from .routes import FailedRequest
        from werkzeug.exceptions import NotFound, InternalServerError, BadRequest, MethodNotAllowed

        # Register blueprints
        app.register_blueprint(auth.b)
        app.register_blueprint(posts.b)
        app.register_blueprint(code.b)
        app.register_blueprint(reviews.b)

        # Handle errors
        @app.errorhandler(404)
        def not_found_eh(e: NotFound):
            return make_response(jsonify(message=e.description, success=False, data={}), e.code)

        @app.errorhandler(405)
        def not_found_eh(e: MethodNotAllowed):
            return make_response(jsonify(message=e.description, success=False, data={}), e.code)

        @app.errorhandler(400)
        def bad_req_eh(e: BadRequest):
            return make_response(jsonify(message=e.description, success=False, data={}), e.code)

        @app.errorhandler(500)
        def bad_req_eh(e: InternalServerError):
            return make_response(jsonify(message=e.description, success=False, data={}), e.code)

        @app.errorhandler(FailedRequest)
        def failed_req_eh(e: FailedRequest):
            return e.response

        db.create_all()

        return app
