import os
import tensorflow as tf
import requests
from database.api import read_model_config
from utils.artifact import download_latest_release

def download_model_link(model_link):
    req = requests.get(model_link)
    with open("/tmp/model.h5", "wb") as file:
        file.write(req.content)

def load_downloaded_model():
    """
    Load the model from the downloaded model
    the model will be saved locally as model.h5

    if found:
        load into model
        delete the model.h5 file
        return model
    else:
        raise Exception
    """

    if os.path.exists("/tmp/model.h5"):
        model = tf.keras.models.load_model("/tmp/model.h5")
        os.remove("/tmp/model.h5")
        return model
    else:
        raise Exception("Model not found")


def load_model():
    """
    Read the config of model and load the model
    if use_release:
        Load the latest release model mentioned by release_name
    else:
        Load the with the given link (Consider the model to be primitive)
        Reset the use_release flag
    """
    try:
        model_config = read_model_config()
        print("Model config:")
        print(model_config)
        model_name = ""
        if model_config["use_release"]:
            model_name = model_config["release_name"]
            download_latest_release(model_name) 
        else:
            model_link = model_config['new_model_link']
            model_name = model_link.split("/")[-1].split(".")[0]
            download_model_link(model_link)
        model = load_downloaded_model()
        return {"model": model, "name": model_name}
    except Exception as ex:
        print(ex)

