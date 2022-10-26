import requests
import shutil
import time
import os
from random import randint
from dotenv import load_dotenv
load_dotenv()

base_endpoint = os.getenv('LC_BASE_ENDPOINT')
endpoint_upload = base_endpoint + "/upload-model"
endpoint_process = base_endpoint + "/process-model"
endpoint_download = base_endpoint + "/jobs"
endpoint_surface_lattices = base_endpoint + '/get-surface-lattices'
endpoint_generate_mesh = base_endpoint + '/generate-tri-mesh'
access_token = os.getenv('LC_API_TOKEN')
project_id = os.getenv('LC_PROJECT_ID')

def build_spec(asset):
    spec = {
    "assets": [],
    "primitives": [
        {
        "type": "TPMSPrim",
        "id": 5,
        "display_name": "TPMS Prim",
        "contents": {
            "type": asset['type'],
            "threshold": 0.001,
            "offset": 0.001,
            "periodicity": 20,
            "shell_thickness": 0.0001
        }
        },
        {
        "type": "BoxPrim",
        "id": 6,
        "display_name": "Box Prim",
        "contents": {
            "extents": {
            "x": 192,
            "y": 120,
            "z": 120
            },
            "xform": {
            "translation": {
                "x": 0,
                "y": 0,
                "z": 60
            },
            "rotation": {
                "_x": 0,
                "_y": 0,
                "_z": 0,
                "_w": 1
            },
            "euler": {
                "x": 0,
                "y": 0,
                "z": 0
            },
            "scale": {
                "x": 1,
                "y": 1,
                "z": 1
            }
            }
        }
        }
    ],
    "slice_operations": [
        {
        "type": "SliceTPMS",
        "id": 7,
        "display_name": "TPMS Slice",
        "contents": {
            "parents": [],
            "tpms_id": 5,
            "box_id": 6
        }
        }
    ],
    "workspace_settings": {
        "printer_settings": {},
        "slice_params": {
        "build_volume": {
            "x": 132,
            "y": 74,
            "z": 200
        },
        "layer_thickness": 0.05,
        "topId": 7
        }
    }
    }
    return spec

def get_surface_lattices():
    url = endpoint_surface_lattices + f"?projectId={project_id}"
    payload = {
        "lattice_tags": [None, None, None]
    }
    headers = {"Authorization": "Bearer " + access_token}
    res = requests.post(url, json=payload, headers=headers,stream=True, verify=True)
    return res.json()

def generate_mesh(spec):
    url = endpoint_generate_mesh + f"?projectId={project_id}"
    payload = {
        "spec": spec,
        "name": "export_custom_mesh",
        "sampler": "default",
        'pos_x': 0,
        'pos_y': 0,
        'pos_z': 0.0,
        'dim_x': 192.0,
        'dim_y': 120.0,
        'z_range': 120.0,
        'grid_res_x': 64,
        'grid_res_y': 64,
        'grid_res_z': 64,
        'closure': 1.0
      }
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
    # Generate some geometry and track the job_id
    lattices = get_surface_lattices()
    for i in range(0, 1):
        rand_index = randint(0,len(lattices['surface_lattices'])-1)
        rand_lattice = lattices['surface_lattices'][rand_index]['contents']
        spec = build_spec(rand_lattice)

        job = generate_mesh(spec)
        job_id = job['job_id']

        # poll the server until job is done
        while not check_and_download(job_id, f"./output/output_{i}.stl"):
            time.sleep(2.0)

if __name__ == "__main__":
    main()


