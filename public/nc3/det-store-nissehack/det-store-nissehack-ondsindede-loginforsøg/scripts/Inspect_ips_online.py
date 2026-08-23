import re
import requests

# Path to the log file
log_file_path = "auth.log"

# Your AbuseIPDB API key
api_key = "insert_api_key_here"

# Regular expression to match successful logins and extract IPs
login_pattern = re.compile(r"Accepted password for \S+ from (\d+\.\d+\.\d+\.\d+)")

# List of private/local IP ranges
private_ip_ranges = [
    re.compile(r"^10\.\d+\.\d+\.\d+$"),
    re.compile(r"^192\.168\.\d+\.\d+$"),
    re.compile(r"^172\.(1[6-9]|2[0-9]|3[0-1])\.\d+\.\d+$"),
]

# Function to check if an IP is local
def is_local_ip(ip):
    return any(pattern.match(ip) for pattern in private_ip_ranges)

# Function to check IP reputation using AbuseIPDB
def check_ip_reputation(ip):
    url = "https://api.abuseipdb.com/api/v2/check"
    querystring = {
        'ipAddress': ip,
        'maxAgeInDays': '90'
    }
    headers = {
        'Accept': 'application/json',
        'Key': api_key
    }
    response = requests.request(method='GET', url=url, headers=headers, params=querystring)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Extract non-local IPs
non_local_ips = set()
with open(log_file_path, "r") as log_file:
    for line in log_file:
        match = login_pattern.search(line)
        if match:
            ip = match.group(1)
            if not is_local_ip(ip):
                non_local_ips.add(ip)

# Check reputation of each non-local IP
for ip in non_local_ips:
    print(f"Checking IP: {ip}")
    result = check_ip_reputation(ip)
    if result and 'data' in result:
        data = result['data']
        if not data["isTor"]:
            print(data)
            print(f"IP: {data['ipAddress']}")
            print(f"Abuse Confidence Score: {data['abuseConfidenceScore']}")
            print(f"countryCode: {data['countryCode']}")
            print(f"ISP: {data['isp']}")
            print(f"Domain: {data['domain']}")
            print(f"Total Reports: {data['totalReports']}")
            print(f"Last Reported At: {data['lastReportedAt']}")
            print("-" * 40)
    else:
        print(f"Failed to retrieve data for IP: {ip}")
