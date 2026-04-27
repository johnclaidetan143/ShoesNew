from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import CartItem, Product

cart_bp = Blueprint("cart", __name__, url_prefix="/api/cart")


@cart_bp.route("/", methods=["GET"])
@jwt_required()
def view_cart():
    """Get user's cart items"""
    user_id = int(get_jwt_identity())
    items = CartItem.query.filter_by(user_id=user_id).all()
    
    if not items:
        return jsonify({"items": [], "total": 0.0}), 200
    
    total = round(sum(i.product.price * i.quantity for i in items), 2)
    return (
        jsonify(
            {
                "items": [i.to_dict() for i in items],
                "total": total,
                "item_count": len(items),
            }
        ),
        200,
    )


@cart_bp.route("/", methods=["POST"])
@jwt_required()
def add_to_cart():
    """Add product to cart"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data.get("product_id"):
        return jsonify({"error": "product_id is required"}), 400
    
    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))

    if quantity < 1:
        return jsonify({"error": "Quantity must be at least 1"}), 400

    product = Product.query.get_or_404(product_id)
    
    if not product.is_active:
        return jsonify({"error": "Product is not available"}), 400
    
    if product.stock < quantity:
        return (
            jsonify(
                {
                    "error": "Insufficient stock",
                    "available": product.stock,
                }
            ),
            400,
        )

    # Check if item already in cart
    item = CartItem.query.filter_by(
        user_id=user_id, product_id=product_id
    ).first()
    
    if item:
        # Check if adding more would exceed stock
        if item.quantity + quantity > product.stock:
            return (
                jsonify(
                    {
                        "error": "Insufficient stock for requested quantity",
                        "available": product.stock,
                        "current_in_cart": item.quantity,
                    }
                ),
                400,
            )
        item.quantity += quantity
    else:
        item = CartItem(
            user_id=user_id, product_id=product_id, quantity=quantity
        )
        db.session.add(item)

    try:
        db.session.commit()
        return jsonify(item.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to add item to cart"}), 500


@cart_bp.route("/<int:item_id>", methods=["PUT"])
@jwt_required()
def update_cart_item(item_id):
    """Update quantity of cart item"""
    user_id = int(get_jwt_identity())
    item = CartItem.query.filter_by(
        id=item_id, user_id=user_id
    ).first_or_404()
    
    data = request.get_json()
    quantity = data.get("quantity")
    
    if quantity is None:
        return jsonify({"error": "quantity is required"}), 400
    
    quantity = int(quantity)
    if quantity < 1:
        return jsonify({"error": "Quantity must be at least 1"}), 400
    
    if item.product.stock < quantity:
        return (
            jsonify(
                {
                    "error": "Insufficient stock",
                    "available": item.product.stock,
                }
            ),
            400,
        )

    item.quantity = quantity
    
    try:
        db.session.commit()
        return jsonify(item.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update cart item"}), 500


@cart_bp.route("/<int:item_id>", methods=["DELETE"])
@jwt_required()
def remove_from_cart(item_id):
    """Remove item from cart"""
    user_id = int(get_jwt_identity())
    item = CartItem.query.filter_by(
        id=item_id, user_id=user_id
    ).first_or_404()
    
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Item removed from cart"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to remove item"}), 500


@cart_bp.route("/clear", methods=["DELETE"])
@jwt_required()
def clear_cart():
    """Clear entire cart"""
    user_id = int(get_jwt_identity())
    
    try:
        CartItem.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return jsonify({"message": "Cart cleared successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to clear cart"}), 500
