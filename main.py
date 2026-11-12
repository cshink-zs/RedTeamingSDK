#################################################################
# This script will trigger a Zscaler AI Red teaming scan.
# You must first configure the following environment variable for it to work.
# OAUTH_CLIENT_ID AND OAUTH_CLIENT_SECRET are obtained from zscaler by creating an API client with the scope redteaming admin
# OAUTH_TOKEN_URL is the URl endpoint like https://[yourtenantid].zslogin.net/oauth2/v1/token where you substitute [yourtenantid] by your zscaler tenant name
# TARGET_ID is the application id that has been configured in red teaming
# TEST_RUN_NAME is the name you want to assign to the test run that will be triggered
################################################################

import os
import sys
import requests


OAUTH_CLIENT_ID = os.environ["OAUTH_CLIENT_ID"]
OAUTH_CLIENT_SECRET = os.environ["OAUTH_CLIENT_SECRET"]
OAUTH_TOKEN_URL = os.environ["OAUTH_TOKEN_URL"]

TARGET_ID=os.environ["TARGET_ID"]
TEST_RUN_NAME=os.environ["TEST_RUN_NAME"]

API_URL = "https://api.zsapi.net/aisecurity/airt/api/v2/test-runs/trigger-new-run"
API_AVAILABLE_PROBES=f"https://api.zsapi.net/private/aisecurity/airt/api/v2/ai-apps/{TARGET_ID}/probe-settings"

def get_access_token():
    response = requests.post(
        OAUTH_TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": OAUTH_CLIENT_ID,
            "client_secret": OAUTH_CLIENT_SECRET,
        },
    )
    response.raise_for_status()
    return response.json()["access_token"]


def check_response_ok(response, context):
    if response.status_code != 200:
        print(f"Error: {context} failed with status {response.status_code}: {response.text}")
        sys.exit(1)


access_token = get_access_token()





headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Bearer {access_token}",
}

response = requests.get(API_AVAILABLE_PROBES, headers=headers)
check_response_ok(response, "Fetching available probes")

##retrieve the avaialble probes from the app configuration
print(f"retrieving available probes for app id: {TARGET_ID}\r\n")

available_probes = response.json()
enabled_probe_ids = [
    probe["probeId"]
    for category in available_probes
    for probe in category["probes"]
    if probe.get("enabled")
]


payload = {
    "targetId": TARGET_ID,
    "probeIds": enabled_probe_ids,
    "name": TEST_RUN_NAME,
    "notifyWhenFinished": True,
    "runAiAnalysis": True,
}

##start a new test runs with available probes
print(f"Triggering test run {TEST_RUN_NAME}\r\n")
response = requests.post(API_URL, headers=headers, json=payload)
check_response_ok(response, "Triggering new test run")

print(response.text)
