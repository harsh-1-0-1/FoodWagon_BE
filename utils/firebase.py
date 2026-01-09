import firebase_admin
from firebase_admin import credentials
from core.config import settings

cred_path = settings.FIREBASE_CREDENTIALS

if not cred_path:
    raise RuntimeError("FIREBASE_CREDENTIALS not set in settings")

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
