import requests
import shutil
import time
import os
from random import randint
from dotenv import load_dotenv
load_dotenv()

base_endpoint = os.getenv('LC_BASE_ENDPOINT')
endpoint_download = base_endpoint + "/jobs"
endpoint_get_slice = base_endpoint + "/generate-slice"
endpoint_get_slice_stack = base_endpoint + "/generate-slice-stack"
endpoint_get_metrics = base_endpoint + '/generate-metrics'
access_token = os.getenv('LC_API_TOKEN')
project_id = os.getenv('LC_PROJECT_ID')

def build_spec():
    spec = {
    "assets": [],
    "primitives": [
        {
        "contents": {
            "offset": 0.001,
            "periodicity": 20,
            "shell_thickness": 0.0001,
            "threshold": 0.001,
            "type": 2
        },
        "display_name": "TPMS Prim",
        "id": 5,
        "type": "TPMSPrim"
        },
        {
        "contents": {
            "extents": {
            "x": 192,
            "y": 120,
            "z": 120
            },
            "xform": {
            "euler": {
                "x": 0,
                "y": 0,
                "z": 0
            },
            "rotation": {
                "_w": 1,
                "_x": 0,
                "_y": 0,
                "_z": 0
            },
            "scale": {
                "x": 1,
                "y": 1,
                "z": 1
            },
            "translation": {
                "x": 0,
                "y": 0,
                "z": 60
            }
            }
        },
        "display_name": "Box Prim",
        "id": 6,
        "type": "BoxPrim"
        }
    ],
    "slice_operations": [
        {
        "contents": {
            "box_id": 6,
            "parents": [
            9
            ],
            "tpms_id": 5
        },
        "display_name": "TPMS Slice",
        "id": 7,
        "type": "SliceTPMS"
        },
        {
        "type": "SliceSphericalTransform",
        "id": 8,
        "display_name": "Spherical Transform",
        "contents": {
            "parents": [],
            "sphere_origin": {
            "x": 100,
            "y": 100,
            "z": 0
            }
        }
        },
        {
        "type": "SliceContourTransform",
        "id": 9,
        "display_name": "Contour Transform",
        "contents": {
            "parents": [
            8
            ],
            "step_size": {
            "x": 10,
            "y": 0.196,
            "z": 0.392
            },
            "scale": {
            "x": 20,
            "y": 20,
            "z": 20
            }
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

def generate_slice(spec):
    url = endpoint_get_slice + f"?projectId={project_id}"
    payload = {
        "spec": spec,
        "name": "export_custom_slice",
        "sampler": "default",
        "format": "png",
        'pos_x': 0,
        'pos_y': 0,
        'pos_z': 60.0,
        'dim_x': 192.0,
        'dim_y': 120.0,
        'res_x': 3840,
        'res_y': 2400,
        'rx': 25.0,
        'ry': 0.0,
        'rz': 0.0
      }
    headers = {"Authorization": "Bearer " + access_token}
    res = requests.post(url, json=payload, headers=headers,stream=True, verify=True)
    return res.json()

def generate_metrics(spec):
    url = endpoint_get_metrics + f"?projectId={project_id}"
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
        'closure': 0.0
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
    spec = build_spec()

    job = generate_slice(spec)
    job_id = job['job_id']
    # poll the server until job is done
    while not check_and_download(job_id, f"./output/slice.png"):
        time.sleep(0.25)

    job = generate_metrics(spec)
    job_id = job['job_id']
    # poll the server until job is done
    while not check_and_download(job_id, f"./output/metrics.json"):
        time.sleep(0.25)

if __name__ == "__main__":
    main()


