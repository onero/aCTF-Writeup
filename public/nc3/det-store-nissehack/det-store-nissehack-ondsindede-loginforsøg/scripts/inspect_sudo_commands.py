import re
from collections import defaultdict

def extract_cron_activity(file_path):
    """
    Extracts and groups CRON activity from the auth.log file.
    """
    cron_activity = defaultdict(list)

    with open(file_path, 'r') as log_file:
        for line in log_file:
            # Match CRON execution lines
            #sudo:   KanelKnaser : TTY=ssh ; PWD=/home/KanelKnaser ; USER=root ; COMMAND=/bin/cat
            cron_match = re.search(r"sudo:   (.+) :\sTTY=(.+) ; PWD=(.+) ; USER=(.+) ; COMMAND=(.+)", line)
            if cron_match:
                user = cron_match.group(1)
                tty = cron_match.group(2)
                pwd = cron_match.group(3)
                target_user = cron_match.group(4)
                command = cron_match.group(5)
                cron_activity[command].append({"user": user, "tty": tty, "target_user": target_user, "pwd": pwd})

    return cron_activity

def display_cron_activity(cron_activity):
    """
    Displays the grouped CRON activity.
    """
    print("\nCRON Activity Grouped by Command:")
    if not cron_activity:
        print("No CRON activity found.")
        return

    for command, entries in cron_activity.items():
        print(f"\nCOMMAND: {command}")
        for entry in entries:
            print(f"  User: {entry['user']}, TTY: {entry['tty']}, PWD: {entry['pwd']}, Target User: {entry['target_user']}")


# Specify the path to the auth.log file
auth_log_path = "auth.log"  # Replace with your file path

# Extract and display CRON activity
cron_data = extract_cron_activity(auth_log_path)
display_cron_activity(cron_data)
