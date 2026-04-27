from app import create_app
from app.extensions import db
from app.models import User, Product, Notification

app = create_app()

with app.app_context():
    db.create_all()

    if not User.query.filter_by(email="admin@pharmaquick.com").first():
        admin = User(name="Admin User", email="admin@pharmaquick.com", role="admin", phone="+1234567890")
        admin.set_password("admin@123")
        db.session.add(admin)

    if not User.query.filter_by(email="customer@example.com").first():
        customer = User(name="Samantha Hope", email="customer@example.com", role="customer", phone="+0987654321")
        customer.set_password("customer@123")
        db.session.add(customer)
        db.session.flush()
        db.session.add(Notification(user_id=customer.id, message="Welcome to PharmaQuick!"))

    if not Product.query.first():
        products = [
            Product(name="Paracetamol 500mg", category="general", price=5.99, stock=120,
                    description="Fast-acting pain relief for fever and headaches."),
            Product(name="Ibuprofen 400mg", category="general", price=7.50, stock=100,
                    description="Anti-inflammatory pain reliever for muscle pain."),
            Product(name="Amoxicillin 250mg", category="antibiotics", price=15.00, stock=60,
                    description="Broad-spectrum antibiotic for bacterial infections."),
            Product(name="Vitamin C 1000mg", category="vitamins", price=12.99, stock=150,
                    description="High-dose vitamin C for immune support."),
            Product(name="Vitamin D3 + K2", category="vitamins", price=18.90, stock=80,
                    description="Supports bone health and calcium absorption."),
            Product(name="Omega-3 Fish Oil", category="vitamins", price=22.00, stock=70,
                    description="Daily omega-3 capsules for heart and brain health."),
            Product(name="Multivitamin Tablets", category="vitamins", price=16.99, stock=100,
                    description="Complete daily multivitamin for adult wellness."),
            Product(name="Newborn Baby Lotion", category="newborn", price=10.25, stock=75,
                    description="Gentle moisturizing lotion for newborn skin."),
            Product(name="Baby Soap Bar", category="newborn", price=7.40, stock=85,
                    description="Natural cleansing soap for delicate newborn skin."),
            Product(name="Baby Diaper Rash Cream", category="newborn", price=11.50, stock=90,
                    description="Zinc oxide cream that protects and heals diaper rash."),
            Product(name="Hydrating Face Cream", category="skincare", price=19.99, stock=80,
                    description="Daily moisturizing cream with soothing botanicals."),
            Product(name="SPF 50 Sunscreen", category="skincare", price=24.00, stock=60,
                    description="Broad-spectrum UVA/UVB protection for daily use."),
            Product(name="Aloe Vera Gel", category="skincare", price=13.50, stock=95,
                    description="Pure aloe vera gel for soothing sunburn and dry skin."),
            Product(name="Probiotic Complex", category="supplements", price=29.90, stock=55,
                    description="10 billion CFU probiotic for gut health."),
            Product(name="Hair Growth Serum", category="general", price=32.00, stock=45,
                    description="Biotin-enriched serum to strengthen and regrow hair."),
        ]
        db.session.add_all(products)

    db.session.commit()
    print("Database seeded successfully.")
    print("Admin:    admin@pharmaquick.com / admin@123")
    print("Customer: customer@example.com  / customer@123")
