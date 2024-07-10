from datetime import datetime, timedelta
from database.database import db

def get_docs_date(date):
    docs = db.collection(f'deploy/{date}/{date}').stream()
    return [doc.to_dict() for doc in docs]

def get_all_docs():
    dates = 14
    all_docs = []
    while dates:
        date = datetime.now() - timedelta(days=dates)
        docs = db.collection(f'deploy/{date.strftime("%Y-%m-%d")}/{date.strftime("%Y-%m-%d")}').stream()
        all_docs.extend(docs)
        dates -= 1
    return [doc.to_dict() for doc in all_docs]