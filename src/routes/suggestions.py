from flask import Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

from . import good_response, FailedRequest, get_from_request
from ..models import Post, User, Suggestion, Code

b = Blueprint("suggestions", __name__, url_prefix="/api/suggestions")


@b.route("/<int:post_id>")
def get_suggestions_of_post(post_id: int):
    p: Post = Post.query.get_or_404(post_id, "Post not found")
    suggestions = Suggestion.query.filter_by(post_id=p.id).order_by(Suggestion.created_at.desc()).all()
    return good_response("Suggestions found", {"suggestions": [s.dict() for s in suggestions]})


@b.route("/<int:post_id>", methods=["POST"])
@jwt_required
def add_suggestion_to_post(post_id: int):
    p: Post = Post.query.get_or_404(post_id, "Post not found")
    u: User = User.query.get(get_jwt_identity()["id"])
    title, content, code_id = get_from_request(["title", "content", "code"], True)
    c: Code = Code.query.get(code_id)
    if not c:
        raise FailedRequest("Code with id " + c.id + " was not found")
    s = Suggestion(title=title, content=content)
    s.code_id = c.id
    s.user_id = u.id
    s.post_id = p.id
    s.save()
    return good_response("Suggestion added", {"suggestion": s.dict()})
