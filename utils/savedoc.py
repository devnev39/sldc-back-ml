from firebase_admin.firestore import SERVER_TIMESTAMP
from database.api import save_doc

def filterDoc(docs: list, key: str, value: str):
    docs = [d for d in docs if d[key] == value]
    return docs[0]

def toNumber(inp: str):
    try:
        return float(inp)
    except Exception as ex:
        print(ex)
        return None

def save_previous_data_to_processed(docs: list):
    """
    This function is used to save data from previous documents to processed
    """

    processed = []

    for doc in docs:
        ts = doc.create_time
        doc = doc.to_dict()
        processed.append({
            'created_at': ts,
            'frequency': toNumber(doc['fields']['frequency']),
            "state_gen": toNumber(filterDoc(doc['stats'], "name", "STATE GEN")['value']),
            "state_demand": toNumber(filterDoc(doc['stats'], "name", "STATE DEMAND")['value'])
        })

    for doc in processed:
        save_doc(doc, 'processed')
