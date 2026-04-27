import os
import sys
import importlib.util

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

APP_PATH = os.path.join(PROJECT_ROOT, "app.py")
spec = importlib.util.spec_from_file_location("main_app", APP_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load Flask app from {APP_PATH}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

app = module.app
