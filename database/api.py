from datetime import datetime, timedelta
from database.database import db

def get_docs_date(date, convert_to_dict = True):
    docs = db.collection(f'deploy/{date}/{date}').stream()
    return [doc.to_dict() for doc in docs] if convert_to_dict else docs

def get_all_docs(convert_to_dict = True, frm: float = None, to: float = None):
    dates = 15
    all_docs = []
    while dates > -1:
        date = datetime.now() - timedelta(days=dates)
        docs = db.collection(f'deploy/{date.strftime("%Y-%m-%d")}/{date.strftime("%Y-%m-%d")}').order_by("created_at").stream()
        all_docs.extend(docs)
        dates -= 1
    return [doc.to_dict() for doc in all_docs] if convert_to_dict else all_docs

def save_doc(doc: dict, collection: str):
    doc_ref = db.collection(collection).document()
    doc_ref.set(doc)