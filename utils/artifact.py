import os
import requests
import json
from database.api import read_model_config, save_model_props
from google.cloud.firestore import SERVER_TIMESTAMP

REPO = os.environ['RELEASE_REPO']
TOKEN = os.environ['RELEASE_API_KEY']

API_URL = f"https://api.github.com/repos/{REPO}/releases"
headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def upload_assets(release_id, model_files):
    UPLOAD_URL_TEMPLATE = f"https://uploads.github.com/repos/{REPO}/releases/{release_id}/assets?name="
    for file_path in model_files:
        file_name = file_path.split("/")[-1]
        upload_url = UPLOAD_URL_TEMPLATE + file_name
        with open(file_path, "rb") as file_data:
            headers.update({
                "Content-Type": "application/octet-stream"
            })
            upload_response = requests.post(upload_url, headers=headers, data=file_data)
            if upload_response.status_code == 201:
                asset = upload_response.json()
                print(f"Uploaded asset: {asset['browser_download_url']}")
            else:
                print(f"Failed to upload asset: {upload_response.json()}")


def download_latest_release(model_name):
    """
    Download the latest release model with the given model_name
    """
    API_KEY = os.environ['RELEASE_API_KEY']
    REPO = os.environ['RELEASE_REPO']

    API_URL = f"https://api.github.com/repos/{REPO}/releases"

    headers = {
        "Authorization": f"token {API_KEY}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(API_URL, headers=headers)

    if response.status_code == 200:
        response = response.json()
    else:
        raise Exception(f"Failed to fetch releases: {response.json()}")
        
    releases = [release for release in response if release['name'].find(model_name) != -1] 

    releases.sort(key=lambda x: x['created_at'], reverse=True)

    url = releases[0]['assets'][0]['browser_download_url']

    req = requests.get(url)

    with open("model.h5", "wb") as file:
        file.write(req.content)

def get_releases():
    response = requests.get(API_URL, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch releases: {response.json()}")
        return []

def get_next_version(model_name):
    releases = get_releases()
    releases = [release for release in releases if release['name'].find(model_name) != -1]
    releases.sort(key=lambda x: x['created_at'], reverse=True)
    if len(releases) == 0:
        return 1
    else:
        return int(releases[0]['tag_name'].split(".")[-1].split("train")[1]) + 1

def create_release(tag_name, release_name, release_description, model_files):
    release_data = {
        "tag_name": tag_name,
        "name": release_name,
        "body": release_description,
        "draft": False,
        "prerelease": False
    }

    response = requests.post(API_URL, headers=headers, data=json.dumps(release_data))
    if response.status_code == 201:
        release = response.json()
        release_id = release["id"]
        print(f"Created release: {release['html_url']}")
        upload_assets(release_id, model_files)

        # os.remove("../model_checkpoint.h5")
    else:
        print(f"Failed to create release: {response.json()}")

def manage_releases():
    releases = get_releases()
    MODEL_TYPES = []

    RELEASES_TO_KEEP = read_model_config()['releases_to_keep']

    for release in releases:
        if release['name'] not in MODEL_TYPES:
            MODEL_TYPES.append(release['name'])
    
    for model_type in MODEL_TYPES:
        model_releases = [release for release in releases if release['name'].startswith(model_type)]
        model_releases.sort(key=lambda x: x['created_at'], reverse=True)
        if len(model_releases) > RELEASES_TO_KEEP:
            for release in model_releases[RELEASES_TO_KEEP:]:
                delete_release(release['id'])

def delete_release(release_id):
    delete_url = f"{API_URL}/{release_id}"
    response = requests.delete(delete_url, headers=headers)
    if response.status_code == 204:
        print(f"Deleted release ID: {release_id}")
    else:
        print(f"Failed to delete release ID {release_id}: {response.json()}")

def push_artifact(model):
    """
    Push the model to the release repo
    """
    model_type = model['name']
    version = get_next_version(model_type)
    tag_name = f"{model_type}.train{version}"
    release_name = model_type

    params = ""
    for key,val in model.items():
        if key != 'model':
            params += f'--{key} : {val}\n'
    
    release_description = f"Version : {version}\n{params}"
    model_files = ["../model_checkpoint.h5"]

    create_release(tag_name, release_name, release_description, model_files)

    del model['model']
    model['created_at'] = SERVER_TIMESTAMP
    save_model_props(model)
    
    manage_releases()