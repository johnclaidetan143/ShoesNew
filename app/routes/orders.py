from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.extensions import db
from app.models import Order, OrderItem, CartItem, Notification, Product, Address, User

orders_bp = Blueprint("orders", __name__, url_prefix="/api/orders")

VALID_STATUSES = {"pending", "processing", "completed", "cancelled"}


def _notify(user_id, message):
    """Create a notification for user"""
    notification = Notification(user_id=user_id, message=message)
    db.session.add(notification)


@orders_bp.route("/checkout", methods=["POST"])
@jwt_required()
def checkout():
    """Create order from cart items"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Get cart items
    cart_items = CartItem.query.filter_by(user_id=user_id).all()

    if not cart_items:
        return jsonify({"error": "Cart is empty"}), 400

    # Validate address if provided
    address_id = data.get("address_id")
    if address_id:
        address = Address.query.filter_by(
            id=address_id, user_id=user_id
        ).first_or_404()

    # Validate stock for all items
    for item in cart_items:
        if item.product.stock < item.quantity:
            return (
                jsonify(
                    {
                        "error": f"Insufficient stock for {item.product.name}",
                        "product_id": item.product_id,
                        "requested": item.quantity,
                        "available": item.product.stock,
                    }
                ),
                400,
            )

    # Calculate total
    total = round(sum(i.product.price * i.quantity for i in cart_items), 2)

    # Create order
    order = Order(
        user_id=user_id, total=total, address_id=address_id, status="pending"
    )
    db.session.add(order)
    db.session.flush()  # Get order.id

    # Create order items and update stock
    try:
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.product.price,
            )
            db.session.add(order_item)
            item.product.stock -= item.quantity

        # Clear cart
        CartItem.query.filter_by(user_id=user_id).delete()

        # Send notification
        _notify(
            user_id,
            f"Order #{order.id} placed successfully. Total: ${total}",
        )

        db.session.commit()
        return jsonify(order.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create order"}), 500


@orders_bp.route("/", methods=["GET"])
@jwt_required()
def order_history():
    """Get order history"""
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    # Admins can see all orders
    if claims.get("role") == "admin":
        orders = Order.query.order_by(Order.created_at.desc()).all()
    else:
        # Customers can only see their orders
        orders = Order.query.filter_by(user_id=user_id).order_by(
            Order.created_at.desc()
        ).all()
    
    return (
        jsonify(
            {
                "orders": [o.to_dict() for o in orders],
                "total_count": len(orders),
            }
        ),
        200,
    )


@orders_bp.route("/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id):
    """Get specific order details"""
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    order = Order.query.get_or_404(order_id)
    
    # Check authorization
    if claims.get("role") != "admin" and order.user_id != user_id:
        return jsonify({"error": "Access denied"}), 403
    
    return jsonify(order.to_dict()), 200


@orders_bp.route("/<int:order_id>/status", methods=["PUT"])
@jwt_required()
def update_order_status(order_id):
    """Update order status (admin only)"""
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    status = data.get("status")
    
    if not status:
        return jsonify({"error": "status is required"}), 400
    
    if status not in VALID_STATUSES:
        return (
            jsonify(
                {"error": f"Status must be one of {VALID_STATUSES}"}
            ),
            400,
        )

    order.status = status
    
    # Send notification to customer
    _notify(
        order.user_id,
        f"Your order #{order.id} status updated to '{status}'.",
    )
    
    try:
        db.session.commit()
        return jsonify(order.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update order status"}), 500


@orders_bp.route("/<int:order_id>/cancel", methods=["POST"])
@jwt_required()
def cancel_order(order_id):
    """Cancel an order"""
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    order = Order.query.get_or_404(order_id)
    
    # Check authorization
    if claims.get("role") != "admin" and order.user_id != user_id:
        return jsonify({"error": "Access denied"}), 403
    
    # Can only cancel pending orders
    if order.status != "pending":
        return (
            jsonify(
                {"error": f"Cannot cancel order with status: {order.status}"}
            ),
            400,
        )
    
    try:
        order.status = "cancelled"
        
        # Restore stock
        for item in order.items:
            item.product.stock += item.quantity
        
        _notify(order.user_id, f"Your order #{order.id} has been cancelled.")
        
        db.session.commit()
        return jsonify(order.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to cancel order"}), 500
