#!/usr/bin/env python3
"""
Create a OneUptime incident and attach a screenshot file.

Usage:
    python3 create_incident.py \
        --title "Server Down" \
        --description "The production server is unreachable" \
        --screenshot /path/to/screenshot.png

Prerequisites:
    1. Create an API Key in OneUptime Dashboard:
       Settings -> API Keys -> Create API Key
       Give it "Create Incident" and "Create File" permissions.
    2. Set the environment variables or edit the config below.
    3. pip install requests
"""

import argparse
import base64
import os
import sys
from pathlib import Path

import requests

ONEUPTIME_URL = os.environ.get("ONEUPTIME_URL", "http://centaurus.caltech.edu")
API_KEY = os.environ.get("ONEUPTIME_API_KEY", "")
PROJECT_ID = os.environ.get("ONEUPTIME_PROJECT_ID", "")

def get_headers():
    return {
        "ApiKey": API_KEY,
        "ProjectID": PROJECT_ID,
        "Content-Type": "application/json",
    }


def upload_file(filepath: str) -> str:
    """Upload a file and return its ID."""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    # Read file as binary and base64 encode
    file_data = path.read_bytes()
    file_b64 = base64.b64encode(file_data).decode("ascii")

    # Determine MIME type
    suffix = path.suffix.lower()
    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
        ".pdf": "application/pdf",
        ".log": "text/plain",
        ".txt": "text/plain",
        ".json": "application/json",
    }
    mime_type = mime_types.get(suffix, "application/octet-stream")

    url = f"{ONEUPTIME_URL}/api/file"
    headers = get_headers()

    payload = {
        "data": {
            "file": file_b64,
            "name": path.name,
            "fileType": mime_type,
            "isPublic": True,
        }
    }

    print(f"Uploading file: {path.name} ({mime_type})...")
    resp = requests.post(url, headers=headers, json=payload)

    if resp.status_code not in (200, 201):
        print(f"Error uploading file: {resp.status_code}")
        print(resp.text)
        sys.exit(1)

    result = resp.json()
    file_id = result.get("_id")
    print(f"File uploaded successfully. ID: {file_id}")
    return file_id


def get_incident_severity_id() -> str:
    """Get the first available incident severity ID."""
    url = f"{ONEUPTIME_URL}/api/incident-severity/get-list"
    headers = get_headers()
    payload = {
        "query": {},
        "select": {"_id": True, "name": True},
        "limit": 10,
        "skip": 0,
    }

    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        print(f"Warning: Could not fetch incident severities: {resp.status_code}")
        print(resp.text)
        return ""

    result = resp.json()
    data = result.get("data", [])
    if not data:
        print("Warning: No incident severities found. Incident will be created without severity.")
        return ""

    # Print available severities
    print("Available severities:")
    for s in data:
        print(f"  - {s.get('name', 'Unknown')}: {s.get('_id')}")

    # Return the first one
    severity = data[0]
    print(f"Using severity: {severity.get('name')}")
    return severity["_id"]


def get_incident_state_id() -> str:
    """Get the 'Created' incident state ID."""
    url = f"{ONEUPTIME_URL}/api/incident-state/get-list"
    headers = get_headers()
    payload = {
        "query": {},
        "select": {"_id": True, "name": True},
        "limit": 10,
        "skip": 0,
    }

    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        print(f"Warning: Could not fetch incident states: {resp.status_code}")
        print(resp.text)
        return ""

    result = resp.json()
    data = result.get("data", [])
    if not data:
        print("Warning: No incident states found.")
        return ""

    # Print available states
    print("Available incident states:")
    for s in data:
        print(f"  - {s.get('name', 'Unknown')}: {s.get('_id')}")

    # Prefer "Created" state, otherwise use first
    for s in data:
        if s.get("name", "").lower() in ("created", "identified", "investigating"):
            print(f"Using state: {s.get('name')}")
            return s["_id"]

    state = data[0]
    print(f"Using state: {state.get('name')}")
    return state["_id"]


def create_incident(title: str, description: str, file_id: str = "") -> dict:
    """Create an incident and optionally attach a screenshot."""
    url = f"{ONEUPTIME_URL}/api/incident"
    headers = get_headers()

    # Build incident data
    incident_data = {
        "projectId": PROJECT_ID,
        "title": title,
    }

    if description:
        incident_data["description"] = description

    # Get severity and state IDs
    severity_id = get_incident_severity_id()
    if severity_id:
        incident_data["incidentSeverityId"] = severity_id

    state_id = get_incident_state_id()
    if state_id:
        incident_data["currentIncidentStateId"] = state_id

    payload = {"data": incident_data}

    print(f"\nCreating incident: {title}...")
    resp = requests.post(url, headers=headers, json=payload)

    if resp.status_code not in (200, 201):
        print(f"Error creating incident: {resp.status_code}")
        print(resp.text)
        sys.exit(1)

    result = resp.json()
    incident_id = result.get("_id")
    print(f"Incident created successfully. ID: {incident_id}")

    # If we have a file, add it as a note with the screenshot
    if file_id and incident_id:
        add_screenshot_note(incident_id, file_id)

    return result


def add_file_note(incident_id: str, filepath: str, file_id: str):
    """Add an internal note to the incident with an attached file."""
    url = f"{ONEUPTIME_URL}/api/incident-internal-note"
    headers = get_headers()

    filename = Path(filepath).name
    file_url = f"{ONEUPTIME_URL}/api/file/image/{file_id}"
    note_content = f"Attached file: [{filename}]({file_url})"

    payload = {
        "data": {
            "projectId": PROJECT_ID,
            "incidentId": incident_id,
            "note": note_content,
        }
    }

    print(f"Attaching {filename} as internal note...")
    resp = requests.post(url, headers=headers, json=payload)

    if resp.status_code not in (200, 201):
        print(f"Warning: Could not add note for {filename}: {resp.status_code}")
        print(resp.text)
    else:
        print(f"File {filename} attached successfully.")


def add_screenshot_note(incident_id: str, file_id: str):
    """Add an internal note to the incident with the screenshot."""
    url = f"{ONEUPTIME_URL}/api/incident-internal-note"
    headers = get_headers()

    # Reference the uploaded file in a markdown note
    file_url = f"{ONEUPTIME_URL}/api/file/image/{file_id}"
    note_content = f"Screenshot attached:\n\n![screenshot]({file_url})"

    payload = {
        "data": {
            "projectId": PROJECT_ID,
            "incidentId": incident_id,
            "note": note_content,
        }
    }

    print("Adding screenshot as internal note...")
    resp = requests.post(url, headers=headers, json=payload)

    if resp.status_code not in (200, 201):
        print(f"Warning: Could not add note: {resp.status_code}")
        print(resp.text)
    else:
        print("Screenshot note added successfully.")


#def main():
#    parser = argparse.ArgumentParser(description="Create a OneUptime incident with a screenshot")
#    parser.add_argument("--title", required=True, help="Incident title")
#    parser.add_argument("--description", default="", help="Incident description")
#    parser.add_argument("--screenshot", default="", help="Path to screenshot file to attach")
#    parser.add_argument("--files", nargs="*", default=[], help="Additional files to attach (e.g. log files)")
#    parser.add_argument("--url", default="", help="OneUptime URL (overrides ONEUPTIME_URL env var)")
#    parser.add_argument("--api-key", default="", help="API Key (overrides ONEUPTIME_API_KEY env var)")
#    parser.add_argument("--project-id", default="", help="Project ID (overrides ONEUPTIME_PROJECT_ID env var)")
#    args = parser.parse_args()
#

def report_incident(title, description, screenshot_path=None, files=None, url=None, api_key=None, project_id=None):
    '''Create a OneUptime incident with optional screenshots and files. 
    This function can be called from other parts of the code to report
    incidents programmatically.'''
    global ONEUPTIME_URL, API_KEY, PROJECT_ID

    if url and api_key and project_id:
        ONEUPTIME_URL = url
        API_KEY = api_key
        PROJECT_ID = project_id

    # Validate required config
    if not API_KEY:
        print("Error: API key is required. Set ONEUPTIME_API_KEY in -init")
        sys.exit(1)
    if not PROJECT_ID:
        print("Error: Project ID is required. Set ONEUPTIME_PROJECT_ID in -init")
        sys.exit(1)

    # Upload screenshot if provided
    screenshot_ids = []
    if screenshot_path:
        for path in screenshot_path:
            if os.path.exists(path):
                fid = upload_file(path)
                screenshot_ids.append((fid))
            else:
                print(f"Warning: Screenshot file not found: {path}")

    # Upload additional files
    extra_file_ids = []
    for f in files:
        fid = upload_file(f)
        extra_file_ids.append((f, fid))

    # Create the incident
    result = create_incident(title, description, screenshot_ids)

    # Attach additional files as notes
    if extra_file_ids and result.get("_id"):
        for filepath, fid in extra_file_ids:
            add_file_note(result["_id"], filepath, fid)

    print(f"\nDone! View incident at: {ONEUPTIME_URL}/dashboard/{PROJECT_ID}/incidents/{result.get('_id')}")
