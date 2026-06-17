import os
import json
import requests

RENDER_API_KEY = "rnd_xdWnb0oAj0SbdhfT3O47vC8tb1w1"
headers = {
    "Authorization": f"Bearer {RENDER_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

try:
    with open("certificates/firebase-key.json", "r") as f:
        firebase_creds = f.read()
except Exception as e:
    print(f"Error reading firebase credentials: {e}")
    firebase_creds = "{}"

payload = {
    "type": "web_service",
    "name": "ambigo-dev-server",
    "repo": "https://github.com/Kaipapurandeswarreddy/dev-server",
    "autoDeploy": "yes",
    "branch": "main",
    "env": "python",
    "serviceDetails": {
        "env": "python",
        "region": "oregon",
        "plan": "free",
        "envSpecificDetails": {
            "buildCommand": "pip install -r requirements.txt",
            "startCommand": "uvicorn main:fastAPI --host 0.0.0.0 --port $PORT"
        },
        "envVars": [
            {
                "key": "MONGODB_URI",
                "value": "mongodb+srv://purandeswarreddykaipa_db_user:fyuProhF6wQFs5y2@cluster0.vjr54xs.mongodb.net/?appName=Cluster0"
            },
            {
                "key": "FIREBASE_CREDENTIALS",
                "value": firebase_creds
            }
        ]
    }
}

print("Creating Web Service on Render...")
response = requests.post("https://api.render.com/v1/services", json=payload, headers=headers)
print(f"Status Code: {response.status_code}")
print(json.dumps(response.json(), indent=2))
