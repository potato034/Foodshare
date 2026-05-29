import importlib.util
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_PATH = os.path.join(BASE_DIR, "Foodshare-main", "main.py")

spec = importlib.util.spec_from_file_location("foodshare_inner_main", APP_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

app = module.app