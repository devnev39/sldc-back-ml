import os
from dotenv import load_dotenv, dotenv_values
from model.selection import load_model
from preprocessing.selection import load_data
from model.engine import train_model
from utils.artifact import push_artifact

load_dotenv()


model = load_model()

data = load_data()

out = train_model(model, data)

push_artifact(out)
