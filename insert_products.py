import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import importlib.util
spec = importlib.util.spec_from_file_location("myapp", os.path.join(os.path.dirname(__file__), "app.py"))
myapp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(myapp)
app = myapp.app
from models import db, Product

with app.app_context():
    new_products = [
        Product(
            name="Reebok Nano X4",
            category="Training",
            price=2899.99,
            stock=45,
            description="Built for versatility with a stable base for lifting and flexible forefoot for cardio.",
            image_url="/static/images/Reebok%20Nano%20X4.jpg"
        ),
        Product(
            name="Under Armour TriBase Reign 6",
            category="Training",
            price=2699.99,
            stock=38,
            description="Designed for heavy lifting with a wide flat base and superior grip for gym performance.",
            image_url="/static/images/UNDER%20ARMOUR.jpg"
        ),
    ]
    for p in new_products:
        exists = Product.query.filter_by(name=p.name).first()
        if not exists:
            db.session.add(p)
            print(f"Added: {p.name}")
        else:
            print(f"Already exists: {p.name}")
    db.session.commit()
    print("Done! Total Training:", Product.query.filter_by(category="Training").count())
