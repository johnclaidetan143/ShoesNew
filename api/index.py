import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import importlib.util
spec = importlib.util.spec_from_file_location("dreamshoe_app", os.path.join(BASE_DIR, "app.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
app = mod.app
