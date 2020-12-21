from flask import Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

from . import get_from_request, good_response, FailedRequest
from ..models import Review, Post, User

b = Blueprint("reviews", __name__, url_prefix="/api/reviews")


@b.route("/<int:post_id>")
def get_reviews_of_post(post_id: int):
    p: Post = Post.query.get_or_404(post_id, "Post not found")
    reviews = Review.query.filter_by(post_id=p.id).order_by(Review.created_at.desc()).all()
    return good_response("Reviews found", {"reviews": [r.dict() for r in reviews]})


@b.route("/<int:post_id>", methods=["POST"])
@jwt_required
def add_review_to_post(post_id: int):
    p: Post = Post.query.get_or_404(post_id, "Post not found")
    u: User = User.query.get(get_jwt_identity()["id"])
    title, content, stars = get_from_request(["title", "content", "stars"], True)
    r = Review(title=title, content=content, stars=stars)
    r.user_id = u.id
    r.post_id = p.id
    r.save()

    return good_response("Review created", {"review": r.dict()})
