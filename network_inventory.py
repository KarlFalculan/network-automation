"""network_inventory.py - simple Cisco device inventory tool."""

devices = [
    {
        "hostname": "R1-HQ",
        "management_ip": "192.168.1.1",
        "device_type": "Cisco ISR 4331 Router",
        "location": "Headquarters",
        "status": "up",
    },
    {
        "hostname": "SW1-Floor2",
        "management_ip": "192.168.1.2",
        "device_type": "Cisco Catalyst 9300 Switch",
        "location": "Building A, Floor 2",
        "status": "up",
    },
    {
        "hostname": "R2-Branch",
        "management_ip": "10.10.10.1",
        "device_type": "Cisco ISR 1100 Router",
        "location": "Branch Office",
        "status": "down",
    },
]


def display_devices(device_list, title):
    """Print devices in a readable block format."""
    print("=" * 50)
    print(title)
    print("=" * 50)
    if not device_list:
        print("No devices found.")
        return
    for number, device in enumerate(device_list, start=1):
        print(f"Device {number}")
        print(f"  Hostname      : {device['hostname']}")
        print(f"  Management IP : {device['management_ip']}")
        print(f"  Device Type   : {device['device_type']}")
        print(f"  Location      : {device['location']}")
        print(f"  Status        : {device['status'].upper()}")
        print("-" * 50)


def get_up_devices(device_list):
    """Return only devices whose status is 'up'."""
    return [d for d in device_list if d["status"].lower() == "up"]


def count_operational(device_list):
    """Count devices that are operational (status 'up')."""
    return len(get_up_devices(device_list))


def main():
    display_devices(devices, "ALL DEVICES")

    up_devices = get_up_devices(devices)
    print()
    display_devices(up_devices, "DEVICES WITH STATUS: UP")

    print()
    print(f"Operational devices: {count_operational(devices)} of {len(devices)}")


if __name__ == "__main__":
    main()