"""restconf_monitor.py - read interface info from a Cisco IOS XE router using RESTCONF."""

import os

import requests
import urllib3

# The sandbox uses a self-signed certificate, so hide the HTTPS warning.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set RESTCONF_USERNAME and RESTCONF_PASSWORD in your shell before running.
HOST = "devnetsandboxiosxec8k.cisco.com"
PORT = 443
USERNAME = os.getenv("RESTCONF_USERNAME")
PASSWORD = os.getenv("RESTCONF_PASSWORD")

URL = f"https://{HOST}:{PORT}/restconf/data/ietf-interfaces:interfaces"

HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json",
}


def get_interfaces():
    """Send a RESTCONF GET request and return the response (or None if it failed)."""
    try:
        response = requests.get(
            URL,
            headers=HEADERS,
            auth=(USERNAME, PASSWORD),
            verify=False,  # self-signed cert on the sandbox
            timeout=10,
        )
        return response
    except requests.exceptions.ConnectTimeout:
        print("Connection failed: the router took too long to answer (timeout).")
    except requests.exceptions.ConnectionError:
        print("Connection failed: could not reach the router. Check the host, port, and internet.")
    except requests.exceptions.RequestException as error:
        print(f"Connection failed: {error}")
    return None


def main():
    if not USERNAME or not PASSWORD:
        print("Set RESTCONF_USERNAME and RESTCONF_PASSWORD environment variables before running.")
        return

    print(f"Connecting to {HOST} ...")
    response = get_interfaces()

    if response is None:
        return

    # Display the HTTP status code
    print(f"HTTP Status Code: {response.status_code}")

    if response.status_code != 200:
        print("Request was not successful.")
        if response.status_code == 401:
            print("Reason: wrong username or password.")
        elif response.status_code == 404:
            print("Reason: the RESTCONF resource was not found.")
        return

    # Read the JSON data and display interface name + enabled status
    data = response.json()
    interfaces = data["ietf-interfaces:interfaces"]["interface"]

    print()
    print(f"{'Interface Name':<25} {'Enabled'}")
    print("-" * 35)
    for interface in interfaces:
        print(f"{interface['name']:<25} {interface['enabled']}")


if __name__ == "__main__":
    main()