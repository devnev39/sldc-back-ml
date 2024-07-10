import pandas as pd
from datetime import datetime
from database.api import get_all_docs, get_docs_date
from google.cloud.firestore import SERVER_TIMESTAMP

# Dowload and save the raw data
# Saving frequency, state gen, state dem to csv

def filter_docs(docs, field, value):
    return next((doc for doc in docs if doc[field] == value), None)

def download_and_save(all_docs = True, date = datetime.now().strftime("%Y-%m-%d")):
    docs = []
    if (all_docs):
        docs = get_all_docs()
    else:
        docs = get_docs_date(date)

    time = []
    freq = []
    state_gen = []
    state_dem = []
    for doc in docs:
        freq.append(doc['fields']['frequency'])
        # time.append(datetime.strptime(f'{d} {t}', '%d/%m/%y %H:%M').timestamp())
        time.append(doc['created_at'].timestamp())
        state_gen.append(filter_docs(doc['stats'], 'name', 'STATE GEN')['value'])
        state_dem.append(filter_docs(doc['stats'], 'name', 'STATE DEMAND')['value'])
    df = pd.DataFrame({'time': time, 'freq': freq, 'state_gen': state_gen, 'state_dem': state_dem})
    name = 'data_all.csv' if all_docs else f'data_{date}.csv'
    df.to_csv(name, index=False)
