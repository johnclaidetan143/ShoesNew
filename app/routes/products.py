from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.extensions import db
from app.models import Product

products_bp = Blueprint("products", __name__, url_prefix="/api/products")

VALID_CATEGORIES = {
    "general",
    "newborn",
    "vitamins",
    "antibiotics",
    "skincare",
    "supplements",
    "equipment",
}


def admin_required(claims):
    """Check if user has admin role"""
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
    return None


@products_bp.route("/", methods=["GET"])
def list_products():
    """Get all active products with optional category filter"""
    category = request.args.get("category")
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)
    
    query = Product.query.filter_by(is_active=True)
    
    if category:
        if category not in VALID_CATEGORIES:
            return (
                jsonify({"error": f"Invalid category: {category}"}),
                400,
            )
        query = query.filter_by(category=category)
    
    products = query.paginate(page=page, per_page=limit)
    return (
        jsonify(
            {
                "products": [p.to_dict() for p in products.items],
                "total": products.total,
                "pages": products.pages,
                "current_page": page,
            }
        ),
        200,
    )


@products_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """Get a specific product by ID"""
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict()), 200


@products_bp.route("/", methods=["POST"])
@jwt_required()
def create_product():
    """Create a new product (admin only)"""
    claims = get_jwt()
    err = admin_required(claims)
    if err:
        return err

    data = request.get_json()
    required_fields = ["name", "price", "category"]
    
    if not all(data.get(f) for f in required_fields):
        return (
            jsonify(
                {"error": f"Required fields: {', '.join(required_fields)}"}
            ),
            400,
        )

    if data["category"] not in VALID_CATEGORIES:
        return (
            jsonify(
                {"error": f"Category must be one of {VALID_CATEGORIES}"}
            ),
            400,
        )

    product = Product(
        name=data["name"],
        description=data.get("description", ""),
        price=float(data["price"]),
        stock=int(data.get("stock", 0)),
        category=data["category"],
        image_url=data.get("image_url"),
    )
    
    try:
        db.session.add(product)
        db.session.commit()
        return jsonify(product.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create product"}), 500


@products_bp.route("/<int:product_id>", methods=["PUT"])
@jwt_required()
def update_product(product_id):
    """Update a product (admin only)"""
    claims = get_jwt()
    err = admin_required(claims)
    if err:
        return err

    product = Product.query.get_or_404(product_id)
    data = request.get_json()

    # Update fields if provided
    if "name" in data:
        product.name = data["name"]
    if "description" in data:
        product.description = data["description"]
    if "price" in data:
        product.price = float(data["price"])
    if "stock" in data:
        product.stock = int(data["stock"])
    if "category" in data:
        if data["category"] not in VALID_CATEGORIES:
            return (
                jsonify(
                    {
                        "error": f"Category must be one of {VALID_CATEGORIES}"
                    }
                ),
                400,
            )
        product.category = data["category"]
    if "image_url" in data:
        product.image_url = data["image_url"]
    if "is_active" in data:
        product.is_active = data["is_active"]

    try:
        db.session.commit()
        return jsonify(product.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update product"}), 500


@products_bp.route("/<int:product_id>", methods=["DELETE"])
@jwt_required()
def delete_product(product_id):
    """Delete a product (admin only) - soft delete"""
    claims = get_jwt()
    err = admin_required(claims)
    if err:
        return err

    product = Product.query.get_or_404(product_id)
    product.is_active = False
    
    try:
        db.session.commit()
        return jsonify({"message": "Product deactivated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete product"}), 500
