from datetime import datetime, timedelta
from database.api import get_all_docs, get_docs_date
from utils.savedoc import save_previous_data_to_processed

def transfer_docs(to: str, before: float = None, after: float = None):
    """
    Transfers docs to said colletion with predifined values extracted from the main raw data

    """
    # get all docs
    docs = get_all_docs(convert_to_dict=False)

    docs = [doc for doc in docs]
    docs.sort(key=lambda x: x.create_time.timestamp())

    print(datetime.fromtimestamp(docs[0].create_time.timestamp()))
    print(datetime.fromtimestamp(docs[-1].create_time.timestamp()))

    transfer_docs = []

    # time = datetime.strptime("2024-07-11 19:15:00", "%Y-%m-%d %H:%M:%S")
    # time = time.timestamp()

    print(len(docs))

    for doc in docs:
        if before and after:
            if doc.create_time.timestamp() <= before and doc.create_time.timestamp() >= after:
                transfer_docs.append(doc)
        elif before:
            if doc.create_time.timestamp() <= before:
                transfer_docs.append(doc)
        elif after:
            if doc.create_time.timestamp() >= after:
                transfer_docs.append(doc)
        else:
            transfer_docs.append(doc)

    print(len(transfer_docs))
    transfer_docs.sort(key=lambda x: x.create_time.timestamp())
    print("Selected doc timestamps (from -> to): ")
    print(datetime.fromtimestamp(transfer_docs[0].create_time.timestamp()))
    print(datetime.fromtimestamp(transfer_docs[-1].create_time.timestamp()))

    save_previous_data_to_processed(transfer_docs)

    print("Transfered !")

