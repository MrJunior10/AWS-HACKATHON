import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
import datetime

if not firebase_admin._apps:
    firebase_json = os.getenv("FIREBASE_CONFIG_JSON")
    if firebase_json:
        try:
            cred_dict = json.loads(firebase_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized successfully from Render Environment Variable.")
        except Exception as e:
            print(f"❌ Firebase Environment Variable Error: {e}")
    else:
        try:
            cred = credentials.Certificate("firebase_credentials.json")
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized successfully from local file.")
        except Exception as e:
            print(f"❌ Firebase File Error: {e}")

try:
    db = firestore.client()
except Exception as e:
    print(f"❌ Firestore Client failed to start: {e}")
    db = None

class DatabaseManager:
    def __init__(self):
        if db:
            self.users_ref = db.collection("users")
        else:
            self.users_ref = None
            print("⚠️ Warning: Database connection missing.")

    def save_plan(self, user_id, roadmap_data, resources_data, topic):
        if not self.users_ref: return
        doc_ref = self.users_ref.document(user_id)
        doc_ref.set({
            "topic": topic,
            "roadmap": roadmap_data,
            "resources": resources_data,
            "created_at": firestore.SERVER_TIMESTAMP,
            "last_active": firestore.SERVER_TIMESTAMP
        }, merge=True)
        print(f"💾 Plan saved for user: {user_id}")

    def load_plan(self, user_id):
        if not self.users_ref: return None
        doc = self.users_ref.document(user_id).get()
        if doc.exists:
            return doc.to_dict()
        return None

    def save_chat(self, user_id, message, sender):
        if not self.users_ref: return
        self.users_ref.document(user_id).collection("chat_history").add({
            "text": message,
            "sender": sender,
            "timestamp": firestore.SERVER_TIMESTAMP
        })

    def save_quiz_result(self, user_id, score, total):
        if not self.users_ref: return
        self.users_ref.document(user_id).update({
            "last_quiz_score": score,
            "last_quiz_total": total,
            "last_quiz_date": firestore.SERVER_TIMESTAMP
        })