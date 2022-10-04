import requests
import shutil
import os
import json
import time
from dotenv import load_dotenv
load_dotenv()

base_endpoint = os.getenv('LC_BASE_ENDPOINT')
endpoint_upload = base_endpoint + "/upload-model"
endpoint_process = base_endpoint + "/process-model"
endpoint_download = base_endpoint + "/jobs"
access_token = os.getenv('LC_API_TOKEN')
project_id = os.getenv('LC_PROJECT_ID')

def upload_model(path):
    url = endpoint_upload + f"?projectId={project_id}"
    headers = {"Authorization": "Bearer " + access_token}
    files = {'file': open(path, 'rb')}
    res = requests.post(url, headers=headers, files=files, verify=True)
    return res.json()

def process_model(path):
    url = endpoint_process + f"?projectId={project_id}"
    payload = {
        "name": "model_process_test",
        "asset": os.path.basename(path),
        "use_cache": False,
        "resolution": 128}
    headers = {"Authorization": "Bearer " + access_token}
    res = requests.post(url, json=payload, headers=headers,stream=True, verify=True)
    return res.json()

def check_and_download(job_id, path):
    url = endpoint_download + f"/{job_id}"
    headers = {"Authorization": "Bearer " + access_token}
    res = requests.get(url,headers=headers,verify=True)
    job_stats = res.json()
    print(job_stats)
    if job_stats['progress'] == 100:
        print("job done! Downloading...")
        url = endpoint_download + f"/{job_id}?download=true"
        res = requests.get(url,headers=headers, stream=True, verify=True)
        if path != None:
            with open(path, 'wb') as out_file:
                shutil.copyfileobj(res.raw, out_file)
        return True
    else:
        return False

def main():
    
    input = "./data/models/fastener.stl"

    # Custom upload of assets if necessary. You can also do this from the webapp.
    mesh_asset = input
    mesh_name = os.path.basename(mesh_asset)
    upload_model(mesh_asset)
    model_job = process_model(mesh_asset)
    # NOTE: after calling process, you need to wait for the job to finish.
    while not check_and_download(model_job['job_id'], None):
        time.sleep(2.0)

if __name__ == "__main__":
    main()


