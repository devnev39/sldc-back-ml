import firebase_admin
from firebase_admin import firestore
from firebase_admin import storage

app = firebase_admin.initialize_app(options={
    "storageBucket": "sldc-live.appspot.com"
})

db = firestore.client(app=app)
bucket = storage.bucket(app=app)

