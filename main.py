import os
from dotenv import load_dotenv, dotenv_values
from model.selection import load_model
from preprocessing.selection import load_data
from model.engine import train_model
from utils.artifact import push_artifact

load_dotenv()

model = load_model()

print(model)

data = load_data()

for key,val in data.items():
    print(f'{key} : {len(val)}')

out = train_model(model, data)

print(out)

push_artifact(out)
