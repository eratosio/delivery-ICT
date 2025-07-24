import json
import random
import string
import requests
import pandas as pd
import os
# Use the function in your main code
old_uid = "cf0cc8d2-8176-47e5-9988-e7431ab3dd0a"
# Generate a random string for the dashboard uid if not provided by user
def generate_random_uid(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


# Recursive function to search and replace values in JSON
def search_and_replace(data, old_value, new_value):
    if isinstance(data, dict):  # If the current element is a dictionary
        for key, value in data.items():
            if isinstance(value, (dict, list)):  # Recursively handle nested structures
                search_and_replace(value, old_value, new_value)
            elif value == old_value:  # Replace matching values
                data[key] = new_value
    elif isinstance(data, list):  # If the current element is a list
        for i in range(len(data)):
            if isinstance(data[i], (dict, list)):  # Recursively handle nested structures
                search_and_replace(data[i], old_value, new_value)
            elif data[i] == old_value:  # Replace matching values
                data[i] = new_value


# Safely replace uids and platform ids in the panels
def replace_uids_and_platform_ids(data, new_uid, platform_id, new_extension_map):
    # Track the uid replacement count
    old_platform_id = "dsapi-succinct-harsh-quit-ict_international.sxc1ob06"
    search_and_replace(data, old_uid, new_uid)
    search_and_replace(data, old_platform_id, platform_id)
    search_and_replace(data, 553, random.randint(100, 999))
    # Iterate through panels to modify relevant fields
    for panel in data.get('panels', []):

        # Check for targets and modify streamid and extensions
        for target in panel.get('targets', []):
            url_options = target.get('url_options', {})
            url = target.get('url', "")

            params = url_options.get('params', [])
            # try:
            #     if old_platform_id in url:
            #         # print('yes')
            #         url = url.replace(old_platform_id, platform_id)
            #         # print(url)
            #         for old_ext, new_ext in new_extension_map.items():
            #             if old_ext in url and new_ext!="":
            #                 url.replace(old_ext, new_ext)
            # except:
            #     pass

            #         target['url'] = url
            #         # Iterate through params to find streamid and replace platform_id and extension
            #         datasource = target.get('datasource', {})

            # Replace uid except for the last occurrence
            # if datasource.get('uid') == "cf0cc8d2-8176-47e5-9988-e7431ab3dd0a":
            #     datasource['uid'] = new_uid

            for param in params:
                if param.get('key') == 'streamid':
                    streamid_value = param.get('value', "")

                    # Check if old platform_id is in streamid and replace it
                    if old_platform_id in streamid_value:
                        new_streamid_value = streamid_value.replace(old_platform_id, platform_id)

                        # Replace the extension based on the map
                        for old_ext, new_ext in new_extension_map.items():
                            if old_ext in new_streamid_value and new_ext != "":
                                new_streamid_value = new_streamid_value.replace(old_ext, new_ext)

                        # Update the param with the new streamid
                        param['value'] = new_streamid_value
                    else:
                        print(f"Platform ID {old_platform_id} not found in streamid {streamid_value}")

    # Replace dashboard title
    data['title'] = dashboard_title
    ext = platform_id.split('.')[-1].upper()
    data['uid'] = generate_random_uid()
    # Handle last uid occurrence (dashboard uid)
    # if data.get('uid'):
    #     # print(data.get('uid'))
    #     data['uid'] = ext #generate_random_uid()  # Replace with a new random uid if needed

    return data


file_path = "../../fetch_platform_from_excel/Ecosearch SRL 2x sfm1x-c.xlsx"  # Replace with the path to your Excel file
df = pd.read_excel(file_path, skiprows=3)

# Extract all values from the second column (index 1) and create a list
platform_ids = df.iloc[:, 2].dropna().tolist()
# platform_ids = ['dsapi-good-silent-parent-ict_international.sx41p201',
#                 'dsapi-simplistic-toothsome-spiritual-ict_international.sx41p202',
#                 'dsapi-nostalgic-gray-sir-ict_international.sx41p203']
# print(platform_ids)
# Configuration: specify the new uid, platform id, and dashboard title
with open("ecosearch_uid.json") as f:
    new_uid = json.load(f)["uid"]
# new_uid = "adff9bc6-9eeb-4df1-8570-93b2987d1e92"  # Replace with your desired uid for the first occurrences

for platform_id in platform_ids:

    # Load the JSON data

    modified_data = {}
    # platform_id = "dsapi-observant-helpless-vehicle-ict_international.sxc1oa01"  # Replace with your desired platform ID
    ext = platform_id.split('.')[-1].upper()
    dashboard_title = f"SAP Flow ({ext})"  # Replace with the new dashboard title
    # Key-value pairs for extensions. Replace the key (current extension) with the corresponding new extension.
    new_extension_map = {
        "calculated-sap-flow-inner": "",  # Replace with your desired extension
        "calculated-sap-flow-outer": "",
        "calculated-sap-flow-remainder": "",
        "cumulative-sap-flow": "",
        "corrected-inner": "",
        "corrected-outer": "",
        "uncorrected-inner": "",
        "uncorrected-outer": "",
        "battery-voltage": "",
        "external-power-supply-voltage": ""
    }

    # Reload the JSON data for each platform_id to reset to the original structure
    with open(
            'sample_grafana_json/sample.json',
            'r') as f:
        try:
            json_data = json.load(f)
            print("JSON loaded successfully:")
        except json.JSONDecodeError as e:
            print("JSON decoding error:", e)
            continue  # Skip to the next iteration if JSON loading fails

    # Modify the JSON structure
    modified_data = replace_uids_and_platform_ids(json_data, new_uid, platform_id, new_extension_map)
    name = f"modified_data_{platform_id}.json"
    print(platform_id)
    # Save the updated JSON to a new file
    os.makedirs("sample_grafana_json", exist_ok=True)
    with open(
            f'sample_grafana_json/{name}',
            'w') as f:
        json.dump(modified_data, f, indent=2)

    # print("JSON modification complete!")

    # exit()
    # Replace with your Grafana instance URL and Service Account token
    GRAFANA_URL = "https://grafana.eratos.com"
    senaps_api_file_path = r"ecosearch_service_account.json"
    f = open(senaps_api_file_path)

    # returns JSON object as a dictionary
    creds = json.load(f)
    SERVICE_ACCOUNT_TOKEN = creds['key']

    # Define headers for authentication
    headers = {
        'Authorization': f'Bearer {SERVICE_ACCOUNT_TOKEN}',
        'Content-Type': 'application/json',
    }

    data = {
        "dashboard": modified_data,
        "folderUid": '',
        "overwrite": True
    }

    # Make the request to create the dashboard
    response = requests.post(f'{GRAFANA_URL}/api/dashboards/db', headers=headers, json=data)

    # Check response status
    if response.status_code == 200:
        print("Dashboard created successfully")
    else:
        print(f"Failed to create dashboard: {response.status_code}")
        print(f"Response content: {response.content}")