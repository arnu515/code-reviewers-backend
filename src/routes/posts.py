from flask import Blueprint, request
from flask_sqlalchemy import Pagination
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import good_response, FailedRequest, get_from_request
from ..models import Post, User, Code

b = Blueprint("posts", __name__, url_prefix="/api/posts")


# Empty route so that we target /api/posts and not /api/posts/
@b.route("")
def get_public_posts():
    try:
        page = int(request.args.get("page", "1"))
        per_page = int(request.args.get("per_page", "10"))
    except ValueError:
        page = 1
        per_page = 10

    p: Pagination = Post.query.order_by(Post.created_at.desc()).filter_by(public=True).paginate(page, per_page)
    return good_response("Posts found", {"posts": [i.dict() for i in p.items]})


@b.route("/<int:pid>")
def get_post_by_id(pid: int):
    p: Post = Post.query.get_or_404(pid, "Post not found")
    return good_response("Post found", {"post": p.dict()})


@b.route("", methods=["POST"])
@jwt_required
def create_post():
    id_ = get_jwt_identity()
    u: User = User.query.get(id_)
    title, desc = get_from_request(["title", "description"], True)
    title = title.strip()
    desc = desc.strip()
    priv, sug = get_from_request(["private", "suggestions"], False)
    p = Post(title=title, description=desc, public=not priv, suggestions_enabled=bool(sug))
    p.user_id = u.id
    p.save()

    return good_response("Post created", {"post": p.dict()})


@b.route("/<int:id_>/author")
@jwt_required
def is_author_of_post(id_: int):
    p: Post = Post.query.get_or_404(id_, "Post not found")
    u: User = User.query.get(get_jwt_identity()["id"])
    if p.user_id != u.id:
        raise FailedRequest("You're not the author", False, 403)
    return good_response("You're the author", True)


@b.route("/<int:id_>/edit", methods=["PUT"])
@jwt_required
def update_post(id_: int):
    p: Post = Post.query.get_or_404(id_, "Post not found")
    u: User = User.query.get(get_jwt_identity()["id"])
    if p.user_id != u.id:
        raise FailedRequest("You're not the author", {}, 403)
    title, desc = get_from_request(["title", "description"], True)
    p.title = title.strip()
    p.description = desc.strip()
    p.save()
    return good_response("Post updated", {"post": p.dict()})


@b.route("/<int:id_>/edit/public", methods=["PATCH"])
@jwt_required
def change_post_visibility(id_: int):
    p: Post = Post.query.get_or_404(id_, "Post not found")
    u: User = User.query.get(get_jwt_identity()["id"])
    if p.user_id != u.id:
        raise FailedRequest("You're not the author", {}, 403)
    public = get_from_request("public", True)
    p.public = bool(public)
    p.save()
    return good_response("Visibility updated", {"post": p.dict()})


@b.route("/<int:id_>/edit/suggestions", methods=["PATCH"])
@jwt_required
def change_post_suggestions(id_: int):
    p: Post = Post.query.get_or_404(id_, "Post not found")
    u: User = User.query.get(get_jwt_identity()["id"])
    if p.user_id != u.id:
        raise FailedRequest("You're not the author", {}, 403)
    sug = get_from_request("suggestions", True)
    p.suggestions_enabled = bool(sug)
    p.save()
    return good_response("Suggestions " + ("enabled" if sug else "disabled"), {"post": p.dict()})


@b.route("/<int:id_>", methods=["DELETE"])
@jwt_required
def delete_post(id_):
    p: Post = Post.query.get_or_404(id_, "Post not found")
    u: User = User.query.get(get_jwt_identity()["id"])
    if p.user_id != u.id:
        raise FailedRequest("You're not the author", {}, 403)
    p.delete()
    return good_response("Post deleted", {"post": p.dict()})


@b.route("/<int:id_>/add/code", methods=["PUT"])
@jwt_required
def add_code_in_post(id_: int):
    p: Post = Post.query.get_or_404(id_, "Post not found")
    u: User = User.query.get(get_jwt_identity()["id"])
    if p.user_id != u.id:
        raise FailedRequest("You're not the author", {}, 403)
    code_ids = get_from_request("code", True)
    for i in code_ids:
        c: Code = Code.query.get(i)
        if not c:
            raise FailedRequest(f"Code with id {i} does not exist")
        p.code.append(c)
        p.save()
    return good_response("Code added", {"post": p.dict()})


@b.route("/<int:id_>/delete/code", methods=["PUT"])
@jwt_required
def remove_code_from_post(id_: int):
    p: Post = Post.query.get_or_404(id_, "Post not found")
    u: User = User.query.get(get_jwt_identity()["id"])
    if p.user_id != u.id:
        raise FailedRequest("You're not the author", {}, 403)
    code_ids = get_from_request("code", True)
    for i in code_ids:
        c: Code = Code.query.get(i)
        if not c:
            raise FailedRequest(f"Code with id {i} does not exist")
        try:
            p.code.remove(c)
            p.save()
        except ValueError:
            raise FailedRequest(f"Code with filename {c.filename} is not there in the post")
    return good_response("Code removed", {"post": p.dict()})
