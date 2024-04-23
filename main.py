import requests

from config import API_KEY

API_URL = "https://api-inference.huggingface.co/models/Organika/sdxl-detector"
headers = {"Authorization": f"Bearer {API_KEY}"}

def query(filename):
    with open(filename, "rb") as f:
        data = f.read()
    response = requests.post(API_URL, headers=headers, data=data)
    return response.json()
