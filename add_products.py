import sys
import os
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import importlib.util
spec = importlib.util.spec_from_file_location("myapp", os.path.join(os.path.dirname(__file__), "app.py"))
myapp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(myapp)
app = myapp.app

from models import db, Product

def img(filename):
    return "/static/images/" + quote(filename)

new_products = [
    Product(name="DimaiGlobal Football Boots", category="Football", price=3499.99, stock=25,
            description="Durable football boots built for all-terrain performance.",
            image_url="/static/images/DimaiGlobal%20Men%27s%20Football%20Boots_football.png"),
    Product(name="Brooks Glycerin 21", category="Training", price=3799.99, stock=40,
            description="Maximum cushioning for long training sessions.",
            image_url="/static/images/Brooks%20Mens%20Glycerin%2021_training.png"),
    Product(name="New Balance FuelCell Rebel V5", category="Training", price=3599.99, stock=35,
            description="Lightweight and responsive for high-intensity training.",
            image_url="/static/images/New%20Balance%20Men%27s%20FuelCell%20Rebel%20V5_training.png"),
]

with app.app_context():
    for p in new_products:
        exists = Product.query.filter_by(name=p.name).first()
        if not exists:
            db.session.add(p)
            print(f"Added: {p.name}")
        else:
            print(f"Already exists: {p.name}")
    db.session.commit()
    print("Done!")
