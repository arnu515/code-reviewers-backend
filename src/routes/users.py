from flask import Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

from . import get_from_request, good_response, FailedRequest
from ..models import User, Post

b = Blueprint("users", __name__, url_prefix="/api/users")
b2 = Blueprint("user", __name__, url_prefix="/api/user")


# /api/user

@b.route("/<string:username>")
def get_user_from_username(username: str):
    u: User = User.query.filter_by(username=username).first_or_404("User not found")
    return good_response("User found", {"user": u.dict()})


@b.route("/<string:username>/posts")
def get_users_posts(username: str):
    u: User = User.query.filter_by(username=username).first_or_404("User not found")
    return good_response("Posts found", {"user": u.dict(), "posts": [p.dict() for p in Post.query
                         .filter_by(user_id=u.id, public=True).order_by(Post.created_at.desc()).all()]})


# /api/user

@b2.route("/profile", methods=["PUT"])
@jwt_required
def update_user_profile():
    u: User = User.query.get(get_jwt_identity()["id"])
    email, username = get_from_request(["email", "username"], True)
    email = email.strip()
    username = username.strip()

    u.email = email
    u.username = username
    u.save()

    return good_response("Profile updated", {"user": u.dict()})


@b2.route("/password", methods=["PATCH"])
@jwt_required
def update_password():
    u: User = User.query.get(get_jwt_identity()["id"])
    p, np, cp = get_from_request(["password", "new_password", "confirm_password"], True)
    if np != cp:
        raise FailedRequest("Passwords don't match")
    if not u.check_password(p):
        raise FailedRequest("Invalid password")
    u.set_password(np)

    return good_response("Password updated", {"user": u.dict()})


@b2.route("/delete", methods=["POST"])
@jwt_required
def delete_account():
    u: User = User.query.get(get_jwt_identity()["id"])
    password = get_from_request("password", True)
    if not u.check_password(password):
        raise FailedRequest("Invalid password")
    for i in u.posts:
        i.delete()
    for i in u.reviews:
        i.delete()
    for i in u.code:
        i.delete()
    for i in u.suggestions:
        i.delete()
    u.delete()
    return good_response("Account deleted", {"user": u.dict()})
