from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.extensions import db
from app.models import User, Address, Notification

user_bp = Blueprint("user", __name__, url_prefix="/api/user")


def _get_current_user():
    """Get current authenticated user"""
    return User.query.get_or_404(int(get_jwt_identity()))


# ────────────── PROFILE ──────────────────────────────────────────────────

@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """Get current user profile"""
    user = _get_current_user()
    return jsonify(user.to_dict()), 200


@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """Update user profile"""
    user = _get_current_user()
    data = request.get_json()

    if "name" in data:
        user.name = data["name"]
    if "phone" in data:
        user.phone = data["phone"]
    if "email" in data:
        # Check if email is already used
        existing = User.query.filter(
            User.email == data["email"], User.id != user.id
        ).first()
        if existing:
            return jsonify({"error": "Email already in use"}), 409
        user.email = data["email"]

    try:
        db.session.commit()
        return jsonify(user.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update profile"}), 500


@user_bp.route("/password", methods=["PUT"])
@jwt_required()
def change_password():
    """Change user password"""
    user = _get_current_user()
    data = request.get_json()

    current_password = data.get("current_password")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    if not current_password or not new_password or not confirm_password:
        return (
            jsonify(
                {
                    "error": "current_password, new_password, and confirm_password are required"
                }
            ),
            400,
        )

    if not user.check_password(current_password):
        return jsonify({"error": "Current password is incorrect"}), 401

    if new_password != confirm_password:
        return jsonify({"error": "New passwords do not match"}), 400

    if len(new_password) < 6:
        return (
            jsonify(
                {"error": "New password must be at least 6 characters"}
            ),
            400,
        )

    user.set_password(new_password)

    try:
        db.session.commit()
        return jsonify({"message": "Password updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update password"}), 500


# ────────────── ADDRESSES ────────────────────────────────────────────────

@user_bp.route("/addresses", methods=["GET"])
@jwt_required()
def list_addresses():
    """Get all user addresses"""
    user_id = int(get_jwt_identity())
    addresses = Address.query.filter_by(user_id=user_id).all()
    return jsonify([a.to_dict() for a in addresses]), 200


@user_bp.route("/addresses", methods=["POST"])
@jwt_required()
def add_address():
    """Add a new address"""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    required_fields = ["street", "city"]
    if not all(data.get(f) for f in required_fields):
        return (
            jsonify({"error": f"Required fields: {', '.join(required_fields)}"}),
            400,
        )

    # If marking as default, unset others
    if data.get("is_default"):
        Address.query.filter_by(user_id=user_id).update(
            {"is_default": False}
        )

    address = Address(
        user_id=user_id,
        label=data.get("label", "Home"),
        street=data["street"],
        city=data["city"],
        state=data.get("state"),
        zip_code=data.get("zip_code"),
        is_default=data.get("is_default", False),
    )

    try:
        db.session.add(address)
        db.session.commit()
        return jsonify(address.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to add address"}), 500


@user_bp.route("/addresses/<int:address_id>", methods=["PUT"])
@jwt_required()
def update_address(address_id):
    """Update an address"""
    user_id = int(get_jwt_identity())
    address = Address.query.filter_by(
        id=address_id, user_id=user_id
    ).first_or_404()
    data = request.get_json()

    # If marking as default, unset others
    if data.get("is_default"):
        Address.query.filter_by(user_id=user_id).update(
            {"is_default": False}
        )

    updatable_fields = ["label", "street", "city", "state", "zip_code", "is_default"]
    for field in updatable_fields:
        if field in data:
            setattr(address, field, data[field])

    try:
        db.session.commit()
        return jsonify(address.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update address"}), 500


@user_bp.route("/addresses/<int:address_id>", methods=["DELETE"])
@jwt_required()
def delete_address(address_id):
    """Delete an address"""
    user_id = int(get_jwt_identity())
    address = Address.query.filter_by(
        id=address_id, user_id=user_id
    ).first_or_404()

    try:
        db.session.delete(address)
        db.session.commit()
        return jsonify({"message": "Address deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete address"}), 500


# ────────────── NOTIFICATIONS ────────────────────────────────────────────

@user_bp.route("/notifications", methods=["GET"])
@jwt_required()
def get_notifications():
    """Get all user notifications"""
    user_id = int(get_jwt_identity())
    notifications = Notification.query.filter_by(user_id=user_id).order_by(
        Notification.created_at.desc()
    ).all()
    return (
        jsonify(
            {
                "notifications": [n.to_dict() for n in notifications],
                "total": len(notifications),
                "unread": sum(1 for n in notifications if not n.is_read),
            }
        ),
        200,
    )


@user_bp.route("/notifications/<int:notif_id>/read", methods=["PUT"])
@jwt_required()
def mark_read(notif_id):
    """Mark notification as read"""
    user_id = int(get_jwt_identity())
    notif = Notification.query.filter_by(
        id=notif_id, user_id=user_id
    ).first_or_404()

    notif.is_read = True

    try:
        db.session.commit()
        return jsonify(notif.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to mark notification as read"}), 500


@user_bp.route("/notifications/read-all", methods=["PUT"])
@jwt_required()
def mark_all_read():
    """Mark all notifications as read"""
    user_id = int(get_jwt_identity())

    try:
        Notification.query.filter_by(user_id=user_id, is_read=False).update(
            {"is_read": True}
        )
        db.session.commit()
        return (
            jsonify({"message": "All notifications marked as read"}),
            200,
        )
    except Exception as e:
        db.session.rollback()
        return (
            jsonify({"error": "Failed to mark notifications as read"}),
            500,
        )


# ────────────── ADMIN: USER MANAGEMENT ────────────────────────────────────

@user_bp.route("/admin/users", methods=["GET"])
@jwt_required()
def list_users():
    """Get all users (admin only)"""
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)
    
    users = User.query.paginate(page=page, per_page=limit)
    return (
        jsonify(
            {
                "users": [u.to_dict() for u in users.items],
                "total": users.total,
                "pages": users.pages,
                "current_page": page,
            }
        ),
        200,
    )


@user_bp.route("/admin/users/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    """Get specific user details (admin only)"""
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


@user_bp.route("/admin/users/<int:user_id>/role", methods=["PUT"])
@jwt_required()
def update_user_role(user_id):
    """Update user role (admin only)"""
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    user = User.query.get_or_404(user_id)
    data = request.get_json()
    new_role = data.get("role")

    if new_role not in {"admin", "customer"}:
        return jsonify({"error": "Role must be 'admin' or 'customer'"}), 400

    user.role = new_role

    try:
        db.session.commit()
        return jsonify(user.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update user role"}), 500


@user_bp.route("/admin/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    """Delete user (admin only)"""
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    user = User.query.get_or_404(user_id)

    # Prevent deleting yourself
    current_user_id = int(get_jwt_identity())
    if user_id == current_user_id:
        return jsonify({"error": "Cannot delete your own account"}), 400

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete user"}), 500
