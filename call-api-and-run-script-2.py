#!/usr/bin/python3

import json
import requests
import subprocess
from datetime import datetime
from requests.utils import default_user_agent
from configobj import ConfigObj


# --- Config ---
config = ConfigObj('call-api-and-run-script.config')
auth_token_file = config['auth_token_file']
server_url      = config['server_url']
redscript       = config['redscript']
changescript    = config['changescript']
log_file        = config['log_file']
response_file   = config['response_file']
healthstatus    = config['healthstatus']
uaaddon         = config['uaaddon']


# --- Functions ---

def read_auth_token(file_path):
    with open(file_path, 'r') as f:
        return f.read().strip()

def read_previous_health_status(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "unknown"

def write_health_status(file_path, status):
    with open(file_path, 'w') as f:
        f.write(status)

def get_api_response(url, token, ua):
    headers = {'Authorization': f'Bearer {token}', 'User-Agent': ua}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            msg = f"HTTP status {response.status_code}, Empty or invalid response"
            return {"error": msg}, msg
        if 'application/json' in response.headers.get('Content-Type', ''):
            try:
                return response.json(), None
            except json.JSONDecodeError:
                return {"error": "Invalid JSON response"}, "Invalid JSON response"
        else:
            return {"error": "Response is not in JSON format"}, "Response is not in JSON format"
    except requests.RequestException as e:
        return {"error": str(e)}, str(e)

def analyze_json(json_data):
    if "error" in json_data:
        return 999, "no valid json received"
    if 'healthDesc' not in json_data:
        return 998, "no healthDesc in json"
    health_notgreen_count = 0
    badmsarray = []
    for item in json_data['healthDesc']:
        if 'briefHealth' in item and 'serviceHealthStatus' in item['briefHealth']:
            if item['briefHealth']['serviceHealthStatus'] != 'HEALTH_GREEN':
                health_notgreen_count += 1
                badmsarray.append(item['serviceName'])
    return health_notgreen_count, ','.join(str(x) for x in badmsarray)

def run_bash_script(script_name, argument):
    subprocess.run([script_name, str(argument)])

def write_to_log(log_file, log_message):
    with open(log_file, 'a') as f:
        f.write(log_message + '\n')

def write_full_response(response_file, response_content):
    with open(response_file, 'w') as f:
        json.dump(response_content, f, indent=4)



# --- Main logic ---

custom_user_agent = default_user_agent() + uaaddon
new_status = "bad"

token           = read_auth_token(auth_token_file)
previous_status = read_previous_health_status(healthstatus)
json_data, error = get_api_response(server_url, token, custom_user_agent)

write_full_response(response_file, json_data)

if not error:
    count, badmsstr = analyze_json(json_data)
    new_status = "healthy" if count == 0 else "bad"
    if count > 0:
        run_bash_script(redscript, f"{count} ({badmsstr})")

if new_status != previous_status:
    status_change_message = f"Status changed from {previous_status} to {new_status}"
else:
    status_change_message = f"Status unchanged ({new_status})"

ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

if not error:
    if count > 0:
        log_message = f"{ts}, {count} ({badmsstr}), {status_change_message}"
    else:
        log_message = f"{ts}, {count}, {status_change_message}"
    write_to_log(log_file, log_message)
else:
    write_to_log(log_file, f"{ts}, Error, {error}, {status_change_message}")
    print("Error during API call:", error)

write_health_status(healthstatus, new_status)

if new_status != previous_status:
    run_bash_script(changescript, new_status)
