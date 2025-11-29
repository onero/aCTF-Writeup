import re
from collections import defaultdict

def extract_failed_logins(file_path):
    """
    Extracts all failed login attempts from the auth.log file,
    including attempts for non-existing users.
    Groups and counts occurrences by username.
    """
    failed_logins = defaultdict(int)  # Dictionary to store counts of failed logins per username

    with open(file_path, 'r') as log_file:
        for line in log_file:
            # Match standard failed logins
            failed_match = re.search(r"Failed password for (\S+) from", line)
            # Match invalid user failed logins
            invalid_user_match = re.search(r"Invalid user (\S+) from", line)

            if failed_match:
                username = failed_match.group(1)
                failed_logins[username] += 1
            elif invalid_user_match:
                username = f"Invalid user: {invalid_user_match.group(1)}"
                failed_logins[username] += 1

    return failed_logins

def display_failed_logins(failed_logins):
    """
    Displays failed login attempts grouped and counted by username.
    """
    print("\nFailed Login Attempts Grouped by Username (Including Non-Existing Users):")
    if failed_logins:
        for username, count in sorted(failed_logins.items(), key=lambda x: -x[1]):
            print(f"  Username: {username}, Failed Attempts: {count}")
    else:
        print("  No failed login attempts found.")

# Specify the path to the auth.log file
auth_log_path = "auth.log"  # Replace with your file path

# Extract and display failed login attempts
failed_logins = extract_failed_logins(auth_log_path)
display_failed_logins(failed_logins)
