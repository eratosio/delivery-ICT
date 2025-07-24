import pandas as pd
import requests
import json

# Load the Excel file, skipping the first three rows to start at row 4
ORG_ID = "ecosearch"
EXCEL_PATH = "Ecosearch SRL 2x sfm1x-c.xlsx"  # Replace with the path to your Excel file
CREDS_PATH = "ict_senaps_key.json"
df = pd.read_excel(EXCEL_PATH, skiprows=3)
# Extract all values from the second column (index 1) and create a list
platform_ids = df.iloc[:, 2].dropna().tolist()

f = open(CREDS_PATH)
creds = json.load(f)
api_cred = creds["key"]

for platform_id in platform_ids:

    url = f"https://senaps.eratos.com/api/sensor/v2/platforms/{platform_id}"
    headers = {
        "apikey": api_cred
    }

    # Prepare payload with values or default to blank/empty if None
    payload = {

    }

    # Send PUT request to the server
    response = requests.request("GET", url, headers=headers, json=payload)
    data = response.json()
    group_ids = [group["id"] for group in data["_embedded"]["groups"]]
    stream_ids_p = [stream["id"] for stream in data["_embedded"]["streams"]]
    stream_ids = [f"{platform_id}.uncorrected-inner-offset", f"{platform_id}.uncorrected-outer-offset",
                  f"{platform_id}.corrected-inner", f"{platform_id}.corrected-outer",
                  f"{platform_id}.sap-velocity-inner", f"{platform_id}.sap-velocity-outer",
                  f"{platform_id}.calculated-sap-flow-outer", f"{platform_id}.calculated-sap-flow-inner",
                  f"{platform_id}.calculated-sap-flow-remainder",
                  f"{platform_id}.cumulative-sap-flow"]
    stream_ids_p.extend(stream_ids)

    for stream_id in stream_ids:
        url = f"https://senaps.eratos.com/api/sensor/v2/streams/{stream_id}"

        payload = {
            "id": stream_id,
            "organisationid": ORG_ID,
            "groupids": group_ids,
            "resulttype": "scalarvalue",
            "streamMetadata": {
                "type": ".ScalarStreamMetaData",
                "interpolationType": "http://www.opengis.net/def/waterml/2.0/interpolationType/Continuous"
            },
            "usermetadata": ""
        }

        headers = {
            "apikey": api_cred,
            "accept": "application/json",
            "content-type": "application/json"
        }

        response = requests.request("PUT", url, headers=headers, json=payload)
        try:
            response.raise_for_status()
            print(f"Successfully updated stream {stream_id}")
        except requests.exceptions.HTTPError as err:
            print(f"Failed to update stream {stream_id}. Response: {err}")

    payload = {
        "id": platform_id,
        "name": platform_id,
        "organisationid": ORG_ID,
        "groupids": group_ids,
        "streamids": stream_ids_p,
        "deployments": [

        ],
        "usermetadata": {}
    }
    url = f"https://senaps.eratos.com/api/sensor/v2/platforms/{platform_id}"
    response = requests.request("PUT", url, headers=headers, json=payload)
    response.raise_for_status()