import re
from collections import defaultdict

def parse_logins_and_logouts(file_path):
    """
    Parses the auth.log file to match login and logout events.
    Logs any login sessions without corresponding logouts.
    """
    login_sessions = []  # Store login events
    unmatched_logins = []  # Logins without matching logouts

    with open(file_path, 'r') as log_file:
        for line in log_file:
            # Match login events
            login_match = re.search(r"Accepted password for (\S+) from (\S+) port (\d+) ssh2", line)
            if login_match:
                username = login_match.group(1)
                ip_address = login_match.group(2)
                port = login_match.group(3)
                timestamp = " ".join(line.split()[:3])  # Extract timestamp

                login_sessions.append({"username": username, "ip": ip_address, "port": port, "timestamp": timestamp})
                continue

            # Match logout events
            logout_match = re.search(r"session closed for user (\S+)", line)
            if logout_match:
                username = logout_match.group(1)
                # Try to find a matching login session for this user
                for session in login_sessions:
                    if session["username"] == username:
                        login_sessions.remove(session)  # Match found; remove from active sessions
                        break
                else:
                    # No matching login session found
                    if username != "root":
                        unmatched_logins.append({"username": username, "timestamp": " ".join(line.split()[:3])})

    return login_sessions, unmatched_logins

def display_results(active_logins, unmatched_logouts):
    """
    Displays results of unmatched logins and unmatched logouts.
    """
    print("\nUnmatched Logins (Logins with no corresponding logouts):")
    if active_logins:
        for session in active_logins:
            print(f"  User: {session['username']}, IP: {session['ip']}, Port: {session['port']}, Time: {session['timestamp']}")
    else:
        print("  None")

    print("\nUnmatched Logouts (Logouts with no corresponding logins):")
    if unmatched_logouts:
        for logout in unmatched_logouts:
            print(f"  User: {logout['username']}, Time: {logout['timestamp']}")
    else:
        print("  None")

# Specify the path to the auth.log file
auth_log_path = "./auth.log" 

# Parse and display unmatched logins and logouts
active_logins, unmatched_logouts = parse_logins_and_logouts(auth_log_path)
display_results(active_logins, unmatched_logouts)
