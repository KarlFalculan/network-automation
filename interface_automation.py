"""interface_automation.py - create Loopback100 on a Cisco IOS XE router using RESTCONF."""

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

# ---- Loopback100 settings (change here if your instructor gives other values) ----
INTERFACE_NAME = "Loopback100"
DESCRIPTION = "Configured by Python RESTCONF"
IP_ADDRESS = "10.100.100.1"
NETMASK = "255.255.255.0"
ENABLED = True

# Delete Loopback100 first so old settings (like a leftover IP) can't clash.
DELETE_FIRST = True

# RESTCONF URL that points to ONE interface (interface=Loopback100)
URL = (
    f"https://{HOST}:{PORT}/restconf/data/"
    f"ietf-interfaces:interfaces/interface={INTERFACE_NAME}"
)

HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json",
}


def build_payload():
    """Step 1: create the JSON configuration payload."""
    return {
        "ietf-interfaces:interface": {
            "name": INTERFACE_NAME,
            "description": DESCRIPTION,
            "type": "iana-if-type:softwareLoopback",
            "enabled": ENABLED,
            "ietf-ip:ipv4": {
                "address": [
                    {
                        "ip": IP_ADDRESS,
                        "netmask": NETMASK,
                    }
                ]
            },
        }
    }


def delete_interface():
    """Remove any old Loopback100 so we start clean (204 = deleted, 404 = did not exist)."""
    try:
        response = requests.delete(
            URL,
            headers=HEADERS,
            auth=(USERNAME, PASSWORD),
            verify=False,
            timeout=15,
        )
    except requests.exceptions.RequestException as error:
        print(f"Cleanup FAILED: could not reach the router ({error})")
        return
    print(f"DELETE HTTP Status Code: {response.status_code}")
    if response.status_code in (200, 204):
        print("Old Loopback100 removed.")
    elif response.status_code == 404:
        print("No old Loopback100 found (that is fine).")
    else:
        print("Cleanup did not work:", response.text)


def configure_interface():
    """Steps 2-4: send the config with PUT and show success or failure."""
    payload = build_payload()
    try:
        response = requests.put(
            URL,
            headers=HEADERS,
            json=payload,
            auth=(USERNAME, PASSWORD),
            verify=False,
            timeout=15,
        )
    except requests.exceptions.RequestException as error:
        print(f"Configuration FAILED: could not reach the router ({error})")
        return False

    print(f"PUT HTTP Status Code: {response.status_code}")

    # 201 = created, 204 = updated (no content), 200 = OK
    if response.status_code == 201:
        print("Configuration SUCCEEDED: Loopback100 was created.")
        return True
    if response.status_code in (200, 204):
        print("Configuration SUCCEEDED: Loopback100 was updated.")
        return True

    print("Configuration FAILED.")
    if response.status_code == 401:
        print("Reason: wrong username or password.")
    else:
        print(response.text)
    return False


def verify_interface():
    """Step 5: GET Loopback100 afterward and check its configuration."""
    print()
    print("Verifying Loopback100 ...")
    try:
        response = requests.get(
            URL,
            headers=HEADERS,
            auth=(USERNAME, PASSWORD),
            verify=False,
            timeout=15,
        )
    except requests.exceptions.RequestException as error:
        print(f"Verification FAILED: could not reach the router ({error})")
        return

    print(f"GET HTTP Status Code: {response.status_code}")
    if response.status_code != 200:
        print("Verification FAILED: could not retrieve Loopback100.")
        return

    interfaces = response.json()["ietf-interfaces:interface"]
    if isinstance(interfaces, list):
        if not interfaces:
            print("Verification FAILED: the response contained no interfaces.")
            return
        interface = interfaces[0]
    else:
        interface = interfaces
    addresses = interface.get("ietf-ip:ipv4", {}).get("address", [])
    ip = addresses[0]["ip"] if addresses else None
    mask = addresses[0]["netmask"] if addresses else None

    print(f"  Name        : {interface.get('name')}")
    print(f"  Description : {interface.get('description')}")
    print(f"  Enabled     : {interface.get('enabled')}")
    print(f"  IP Address  : {ip}")
    print(f"  Netmask     : {mask}")

    if ip == IP_ADDRESS and mask == NETMASK and interface.get("enabled") == ENABLED:
        print("Verification PASSED: the router matches the configuration we sent.")
    else:
        print("Verification FAILED: the router values do not match what we sent.")


def main():
    if not USERNAME or not PASSWORD:
        print("Set RESTCONF_USERNAME and RESTCONF_PASSWORD environment variables before running.")
        return

    if DELETE_FIRST:
        delete_interface()
        print()
    if configure_interface():
        verify_interface()


if __name__ == "__main__":
    main()