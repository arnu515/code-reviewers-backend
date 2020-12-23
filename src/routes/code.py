from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import List

from . import good_response, FailedRequest, get_from_request
from ..models import User, Code
from ..util import generate_string, files

b = Blueprint("code", __name__, url_prefix="/api/code")


@b.route("")
@jwt_required
def get_code_by_user():
    u: User = User.query.get(get_jwt_identity()["id"])
    c: List[Code] = Code.query.filter_by(user_id=u.id).order_by(Code.created_at.desc()).all()
    return good_response("Code found", {"code": [i.dict() for i in c]})


@b.route("", methods=["POST"])
@jwt_required
def add_code():
    u: User = User.query.get(get_jwt_identity()["id"])
    lang, code = get_from_request(["language", "code"], True)
    filename: str = get_from_request("filename", False) or generate_string()
    lang = lang.lower().strip()
    filename = filename.strip()
    if Code.query.filter_by(filename=filename, user_id=u.id).first():
        raise FailedRequest(f"File with name {filename} already exists!")

    path, local = files.create_encrypted_file(filename, code, username=u.username)
    c = Code(language=lang, filename=filename, path=path, local=local)
    c.user_id = u.id
    c.save()

    return good_response("Code added", {"code": c.dict()})


@b.route("/fromfile", methods=["POST"])
@jwt_required
def add_code_from_file():
    u: User = User.query.get(get_jwt_identity()["id"])
    lang = request.form.get("language")
    filename = request.form.get("filename", generate_string())
    lang = lang.lower().strip()
    filename = filename.strip()

    if not lang or not filename:
        raise FailedRequest("Fill out all fields!")

    if not request.files or not request.files.get("file"):
        raise FailedRequest("Please attach a script file with UTF-8 encoding")

    if Code.query.filter_by(filename=filename).first():
        raise FailedRequest(f"File with name {filename} already exists")

    try:
        code = request.files["file"].stream.read().decode()
    except UnicodeDecodeError:
        raise FailedRequest("Please attach a script file with UTF-8 encoding")

    path, local = files.create_encrypted_file(filename, code, username=u.username)
    c = Code(language=lang, filename=filename, path=path, local=local)
    c.user_id = u.id
    c.save()

    return good_response("Code added from file", {"code": c.dict()})


@b.route("/<int:id_>")
def get_code_by_id(id_: int):
    c: Code = Code.query.get_or_404(id_, "Code not found")
    return good_response("Code found",
                         {"code": c.dict(), "content": files.get_encrypted_file_contents(c.filename, local=c.local)})


@b.route("/<int:id_>", methods=["PUT"])
@jwt_required
def update_code(id_: int):
    u: User = User.query.get(get_jwt_identity()["id"])
    c: Code = Code.query.get(id_)
    if c.user_id != u.id:
        raise FailedRequest("You're not the owner", {}, 403)

    lang, code, filename = get_from_request(["language", "code", "filename"], True)
    lang = lang.lower().strip()
    filename = filename.strip()

    path, local = files.create_encrypted_file(filename, code, username=u.username)

    c.filename = filename
    c.path = path
    c.local = local
    c.language = lang
    c.save()

    return good_response("Code updated", {"code": c.dict(), "content": code})


@b.route("/<int:id_>/author")
@jwt_required
def check_if_code_author(id_: int):
    u: User = User.query.get(get_jwt_identity()["id"])
    c: Code = Code.query.get_or_404(id_, "Code not found")
    if c.user_id != u.id:
        raise FailedRequest("You're not the owner", {}, 403)
    return good_response("You're the owner", {"code": c.dict()})
