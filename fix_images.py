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

with app.app_context():
    fixes = {
        "Nike Metcon 9": "/static/images/" + quote("Nike Metcon 9_training.png"),
        "Brooks Glycerin 21": "/static/images/" + quote("Brooks Men's Glycerin 21_training.png"),
    }
    for name, url in fixes.items():
        p = Product.query.filter_by(name=name).first()
        if p:
            p.image_url = url
            print(f"Fixed: {name} -> {url}")
        else:
            print(f"Not found: {name}")
    db.session.commit()
    print("Done!")
