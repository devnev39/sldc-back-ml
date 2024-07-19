from database.api import read_data_config, get_all_parsed_docs, get_parsed_docs_between
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def add_columns(df):
  df['hour'] = df.index.hour
  df['dayOfWeek'] = df.index.day_of_week
  df['month'] = df.index.month

  return df

def preprocess_df(df, remove_below=15000, remove_above=30000):
  df = df[df['state_demand'] > remove_below]
  df = df[df['state_demand'] < remove_above]
  return df

def split_series(series, window_size, n_future):
  # Return single feature in y

  # Multivariate input -> single output

  # Series shape => (samples, features)
  # X shape => (samples, window_size, features)
  # Y shape => (samples, output)

  X = []
  y = []

  for i in range(len(series)):
    start = i
    end = start + window_size
    label = end + n_future

    if label > len(series):
      break

    X.append(series[start:end].to_numpy())
    y.append(series[end:label].to_numpy())

  return np.array(X), np.array(y)[:, :, 0]

def rescale_output(output, mean, std):
  return (output*std) + mean

def load_data():
    """
    load the data according to the configuration
    
    Return:
        data: dict
        {
            X_train: [],
            y_train: [],
            X_test: [],
            y_test: [],
            X_val: [],
            y_val: [],
            train_mean: [],
            train_std: []
        }

        train:test:val = 0.7:0.2:0.1
    """
    
    data_conf = read_data_config()
    window_size = data_conf["window_size"]
    """
    1. Dowload the data
    2. Parse all data to list
    3. Parse list to pandas dataframe
    4. Preprocess and remove inconsistent data
    5. Add feature columns
    6. Split the data
    7. Return the data
    """

    data = []

    if data_conf['use_all_data']:
        docs = get_all_parsed_docs()

        for doc in docs:
            for item, value in doc.items():
                value['created_at'] = value['created_at'].timestamp() + (5*60*60) + (30*60)
                data.append(value)
        data.sort(key = lambda i : i['created_at'], reverse=True)
    else:
        frm = int((datetime.now() - timedelta(days=data_conf['use_latest'])).timestamp())
        to = int(datetime.now().timestamp())

        docs = get_parsed_docs_between(frm, to)

        for doc in docs:
            for item, value in doc.items():
                value['created_at'] = value['created_at'].timestamp() + (5*60*60) + (30*60)
                data.append(value)
        data.sort(key = lambda i : i['created_at'], reverse=True)

    df = pd.DataFrame.from_records(data)
    df.index = df['created_at']
    df = df.sort_index()
    df.drop(columns=["created_at", "frequency", "state_gen"], axis=1, inplace=True)
    df.index = pd.to_datetime(df.index, unit="s")

    df = add_columns(df)
    df = preprocess_df(df)

    TRAIN = 0.7
    VALID = 0.9
    TEST = 0.8
    FUTURE = 1

    n = len(df)
    train_data = df[0:int(n*TRAIN)]
    val_data = df[int(n*TRAIN):int(n*VALID)]
    test_data = df[int(n*TEST):n]

    train_mean = train_data.mean()
    train_std = train_data.std()

    train_df = (train_data - train_mean) / train_std
    val_df = (val_data - train_mean) / train_std
    test_df = (test_data - train_mean) / train_std

    X_train, y_train = split_series(train_df, window_size, FUTURE)
    X_val, y_val = split_series(val_df, window_size, FUTURE)
    X_test, y_test = split_series(test_df, window_size, FUTURE)

    return {
        'X_train': X_train,
        'y_train': y_train,
        'X_test': X_test,
        'y_test': y_test,
        'X_val': X_val,
        'y_val': y_val,
        'train_mean': train_mean,
        'train_std': train_std
    }
