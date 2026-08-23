import re

def parse_logins_and_logouts_by_thread(file_path):
    """
    Parses the auth.log file to match login and logout events by thread ID.
    Logs any login sessions without corresponding logouts.
    """
    login_sessions = {}  # Store login events by thread ID
    unmatched_logouts = []  # Logouts without matching logins



    with open(file_path, 'r') as log_file:

        matched = 0
        for line in log_file:
            # Debug: Print each line being processed
            # print(f"Processing line: {line.strip()}")

            # Match login events
            login_match = re.search(r"sshd\[(\d+)\]:\sAccepted\spassword\sfor\s(\S+)\sfrom\s(\S+)\sport\s(\d+)", line)
            if login_match:
                thread_id = login_match.group(1)
                username = login_match.group(2)
                ip_address = login_match.group(3)
                port = login_match.group(4)
                timestamp = " ".join(line.split()[:3])  # Extract timestamp
                login_sessions[thread_id] = {
                    "username": username,
                    "ip": ip_address,
                    "port": port,
                    "timestamp": timestamp,
                }
                # print(f"Matched login: Thread ID={thread_id}, User={username}, IP={ip_address}, Port={port}, Time={timestamp}")
                matched +=1
                continue

            # Match logout events
            logout_match = re.search(r"sshd\[(\d+)\]:\spam_unix\(sshd:session\):\ssession\sclosed\sfor\suser\s(\S+)", line)
            if logout_match:
                thread_id = logout_match.group(1)
                username = logout_match.group(2)
                # print(f"Matched logout: Thread ID={thread_id}, User={username}")
                # Try to find a matching login session by thread ID
                if thread_id in login_sessions:
                    del login_sessions[thread_id]  # Match found; remove from active sessions
                else:
                    # No matching login session found
                    unmatched_logouts.append({"username": username, "thread_id": thread_id, "timestamp": " ".join(line.split()[:3])})

    print("Matched logins: " + str(matched))
    return login_sessions, unmatched_logouts

def display_results(active_logins, unmatched_logouts):
    """
    Displays results of unmatched logins and unmatched logouts.
    """
    print("\nUnmatched Logins (Logins with no corresponding logouts):")
    if active_logins:
        for thread_id, session in active_logins.items():
            print(f"  Thread ID: {thread_id}, User: {session['username']}, IP: {session['ip']}, Port: {session['port']}, Time: {session['timestamp']}")
    else:
        print("  None")

    print("\nUnmatched Logouts (Logouts with no corresponding logins):")
    if unmatched_logouts:
        for logout in unmatched_logouts:
            print(f"  Thread ID: {logout['thread_id']}, User: {logout['username']}, Time: {logout['timestamp']}")
    else:
        print("  None")

# Specify the path to the auth.log file
auth_log_path = "./auth.log"  # Replace with your file path

# Parse and display unmatched logins and logouts
active_logins, unmatched_logouts = parse_logins_and_logouts_by_thread(auth_log_path)
display_results(active_logins, unmatched_logouts)
