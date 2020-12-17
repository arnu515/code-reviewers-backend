from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import good_response, FailedRequest, get_from_request
from ..models import User, Code
from ..util import generate_string, files

b = Blueprint("code", __name__, url_prefix="/api/code")


@b.route("", methods=["POST"])
@jwt_required
def add_code():
    u: User = User.query.get(get_jwt_identity()["id"])
    lang, code = get_from_request(["language", "code"], True)
    filename: str = get_from_request("filename", False) or generate_string()

    path, local = files.create_encrypted_file(filename, code)
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

    if not lang or not filename:
        raise FailedRequest("Fill out all fields!")

    if not request.files or not request.files.get("file"):
        raise FailedRequest("Please attach a script file with UTF-8 encoding")
    try:
        code = request.files["file"].stream.read().decode()
    except UnicodeDecodeError:
        raise FailedRequest("Please attach a script file with UTF-8 encoding")

    path, local = files.create_encrypted_file(filename, code)
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

    path, local = files.create_encrypted_file(filename, code)

    c.filename = filename
    c.path = path
    c.local = local
    c.lang = lang
    c.save()

    return good_response("Code updated", {"code": c.dict(), "content": code})
