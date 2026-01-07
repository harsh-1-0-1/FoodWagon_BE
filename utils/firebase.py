import os
import firebase_admin
from firebase_admin import credentials

cred_path = os.getenv("FIREBASE_CREDENTIALS")

if not cred_path:
    raise RuntimeError("FIREBASE_CREDENTIALS env var not set")

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
