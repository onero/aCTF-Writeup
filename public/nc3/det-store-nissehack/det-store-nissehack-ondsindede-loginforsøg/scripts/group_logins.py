import re
from collections import defaultdict
from ipaddress import ip_address, ip_network

# Define private IP ranges
PRIVATE_NETWORKS = [
    ip_network("10.0.0.0/8"),
    ip_network("172.16.0.0/12"),
    ip_network("192.168.0.0/16"),
]

def is_private_ip(ip):
    """Determine if an IP address is private."""
    ip_obj = ip_address(ip)
    return any(ip_obj in network for network in PRIVATE_NETWORKS)

def parse_successful_logins(file_path):
    """
    Parses the auth.log file to extract successful login events,
    grouping them by username and IP address (internal vs external).
    """
    login_counts = {
        "internal": defaultdict(lambda: defaultdict(int)),
        "external": defaultdict(lambda: defaultdict(int)),
    }

    with open(file_path, 'r') as log_file:
        for line in log_file:
            # Match lines with successful logins
            match = re.search(r"Accepted password for (\S+) from (\S+)", line)
            if match:
                username = match.group(1)
                ip_address = match.group(2)
                ip_type = "internal" if is_private_ip(ip_address) else "external"
                login_counts[ip_type][username][ip_address] += 1

    return login_counts

def display_login_counts(login_counts):
    """
    Displays the grouped and counted login information by IP type.
    """
    for ip_type, users in login_counts.items():
        print(f"\n{ip_type.capitalize()} IP Logins:")
        if not users:
            print("  No logins found.")
            continue

        for username, ips in users.items():
            print(f"\n  User: {username}")
            for ip, count in ips.items():
                print(f"    IP: {ip} - Logins: {count}")

# Specify the path to the auth.log file
auth_log_path = "./auth.log"  # Replace with your file path

# Parse and display the successful login counts
login_data = parse_successful_logins(auth_log_path)
display_login_counts(login_data)
