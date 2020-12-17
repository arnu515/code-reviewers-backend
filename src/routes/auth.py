from flask import Blueprint, make_response, jsonify
from flask_jwt_extended import create_access_token, get_jti, get_jwt_identity, jwt_required, get_raw_jwt

from . import get_from_request, FailedRequest, good_response
from ..util import store_token, revoke_token
from ..models import User

b = Blueprint("auth", __name__, url_prefix="/api/auth")


@b.route("/login", methods=["POST"])
def login():
    email, password = get_from_request(["email", "password"], True)
    email = email.strip()

    if not email:
        raise FailedRequest("Property \"email\" missing in request body")

    u = User.query.filter_by(email=email).first()
    if u is None:
        raise FailedRequest("User doesn't exist")

    if not u.check_password(password):
        raise FailedRequest("Invalid password")

    token = create_access_token(dict(id=u.id))
    store_token(get_jti(token))
    res = good_response("Logged in successfully", dict(token=token, user=u.dict()))
    return res


@b.route("/register", methods=["POST"])
def register():
    email, password, username = get_from_request(["email", "password", "username"], True)
    email = email.strip()
    username = username.strip()

    if not email:
        raise FailedRequest("Property \"email\" missing in request body")

    if not username:
        raise FailedRequest("Property \"username\" missing in request body")

    if User.query.filter_by(email=email).first():
        raise FailedRequest("Email already registered!")

    if User.query.filter_by(username=username).first():
        raise FailedRequest("Username already registered!")

    u = User.new(email, password, username)
    token = create_access_token(dict(id=u.id))
    store_token(get_jti(token))
    res = good_response("Registered successfully", dict(token=token, user=u.dict()))
    return res


@b.route("/user")
@jwt_required
def get_user():
    id_ = get_jwt_identity()
    u = User.query.get(id_["id"])
    if not u:
        res = make_response(jsonify(dict(success=False, data={}, message="Invalid token")), 401)
        return res
    return good_response("User found", dict(user=u.dict()))


@b.route("/logout", methods=["DELETE"])
@jwt_required
def logout():
    res = good_response("Logged out successfully")
    revoke_token(get_raw_jwt()["jti"])
    return res
