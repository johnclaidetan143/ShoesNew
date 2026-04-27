from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from app.extensions import db
from app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

VALID_ROLES = {"admin", "customer"}


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ["name", "email", "password"]
    if not all(data.get(f) for f in required_fields):
        return (
            jsonify({"error": "name, email, and password are required"}),
            400,
        )

    # Check if email already exists
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    # Validate role
    role = data.get("role", "customer")
    if role not in VALID_ROLES:
        return (
            jsonify({"error": f"Role must be one of {VALID_ROLES}"}),
            400,
        )

    # Create new user
    user = User(
        name=data["name"],
        email=data["email"],
        role=role,
        phone=data.get("phone", None),
    )
    user.set_password(data["password"])
    
    try:
        db.session.add(user)
        db.session.commit()
        return (
            jsonify(
                {
                    "message": "User registered successfully",
                    "user": user.to_dict(),
                }
            ),
            201,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Registration failed"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login user and return JWT token"""
    data = request.get_json()
    
    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "email and password are required"}), 400

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(
        identity=str(user.id), additional_claims={"role": user.role}
    )
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return (
        jsonify(
            {
                "message": "Login successful",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user.to_dict(),
            }
        ),
        200,
    )


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(int(user_id))
    
    new_access_token = create_access_token(
        identity=str(user.id), additional_claims={"role": user.role}
    )
    
    return jsonify({"access_token": new_access_token}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """Get current user profile"""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(int(user_id))
    return jsonify(user.to_dict()), 200
