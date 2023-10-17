import json
import requests
from requests.exceptions import Timeout

req_error = "No errors"

def get(url, headers=None, timeout=None):
    return requests.get(url, headers=headers, timeout=timeout)

def post(url, data=None, headers=None, timeout=None):
    return requests.post(url, data=data, headers=headers, timeout=timeout)

def get_data(url) -> str:
    headers = {'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0'}
    try:
        req = get(url, headers=headers, timeout=20)
    except Timeout:
        req_error = "Timeout"
    except Exception as e:
        req_error = e
    else:
        return str(req.text)

def get_json(url:str) -> str:
    try:
        return json.loads(get_data(url))
    except ValueError as e:
        return "{}"

def post_json(url:str) -> str:
    try:
        return json.loads(post(url).text)
    except ValueError as e:
        return "{}"
    