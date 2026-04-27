import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Force load app.py not app/ folder
import importlib.util
spec = importlib.util.spec_from_file_location("myapp", os.path.join(os.path.dirname(__file__), "app.py"))
myapp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(myapp)
app = myapp.app

from models import db, Product

with app.app_context():
    prices = {
        'Running':    [3299.99, 3599.99, 3999.99, 4299.99],
        'Basketball': [3499.99, 3999.99, 4499.99, 4999.99, 3799.99, 4199.99, 4699.99, 3599.99],
        'Training':   [3199.99, 3499.99, 3799.99, 4099.99],
        'Football':   [3999.99, 4299.99, 4599.99, 4999.99, 3699.99],
        'Lifestyle':  [3099.99, 3399.99, 3699.99, 3999.99],
    }
    for cat, price_list in prices.items():
        products = Product.query.filter_by(category=cat).order_by(Product.id).all()
        for i, product in enumerate(products):
            product.price = price_list[i % len(price_list)]
    db.session.commit()
    print("Done! All prices updated to 3k-5k range.")
