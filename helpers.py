import os
import requests
from dotenv import load_dotenv
load_dotenv()
import random
from datetime import datetime
import json

# this keeps track of the creation queries that have been made under the developers OpenAPI key and allows further development of the tool. No further data is tracked.
class Save:    
    @staticmethod
    def save_on_redis(zimreq):
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        def generate_key():
            return ''.join([random.choice('23456789abcdefghjklmnopqrstuvwxyz') for _ in range(8)])

        key = "zim-gen-req:" + generate_key()
        body = {"created":f"{datetime.now()}","requested":zimreq}
       
        response = requests.post(f'https://fastapi-redis-crud.vercel.app/create_dict?key={key}', headers=headers, data=json.dumps(body))

        print(response.json())
        