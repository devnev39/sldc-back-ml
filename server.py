import os
from fastapi import FastAPI, status, Response
from model.selection import load_model
from preprocessing.selection import load_data
from model.engine import train_model
from utils.artifact import push_artifact

app = FastAPI()

@app.get("/")
def read_root(response: Response):
    model = load_model()
    print(model)
    data = load_data()
    for key,val in data.items():
        print(f'{key} : {len(val)}')
    out = train_model(model, data)

    if os.path.exists("/tmp/model_checkpoint.h5"):
        print("Model found !")
    else:
        print("Model not found !")

    print(out)
    push_artifact(out)
    
    response.status_code = status.HTTP_201_CREATED
