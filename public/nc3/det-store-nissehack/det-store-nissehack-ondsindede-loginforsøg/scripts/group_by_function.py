import re
from collections import Counter

# Path to the auth.log file
log_file_path = "./auth.log"

# Define patterns to match generalized log types
patterns = {
    "Failed password": r"Failed password for invalid user \S+ from \S+ port \d+ ssh2",
    "Failed password user known": r"Failed password for root from \S+ port \d+ ssh2",
    "Accepted password": r"Accepted password for \S+ from \S+ port \d+ ssh2",
    "Session opened": r"pam_unix\(sshd:session\): session opened for user \S+ by \(uid=0\)",
    "Session closed": r"pam_unix\(sshd:session\): session closed for user \S+",
    "Authentication failure with user":    r"pam_unix\(sshd:auth\): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=.* user=root",
    "Authentication failure without user": r"pam_unix\(sshd:auth\): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=.*",
    "Invalid user": r"Invalid user \S+ from \S+ port \d+",
    "Check pass, user unknown": r"pam_unix\(sshd:auth\): check pass; user unknown",
    "Command executed via sudo": r"sudo: \s*\S+ : TTY=ssh ; PWD=\S+ ; USER=\S+ ; COMMAND=.*",
    "CRON session opened": r"pam_unix\(cron:session\): session opened for user \S+ by \(uid=0\)",
    "CRON session closed": r"pam_unix\(cron:session\): session closed for user \S+",
    "Disconnected (preauth)": r"Disconnected from authentication user \S+ \S+ port \d+ \[preauth\]",
    "Received disconnect": r"Received disconnect from \S+ port \d+:\d+: Bye Bye \[preauth\]",
    "Started OpenBDS": r"Started OpenBSD Secure Shell server.",
    "Stopped OpenBDS": r"Stopped OpenBSD Secure Shell server."
}

# Counter to store matches
log_counter = Counter()

# Read and process the log file
with open(log_file_path, "r") as file:
    for line in file:
        matched = False
        for category, pattern in patterns.items():
            if re.search(pattern, line):
                log_counter[category] += 1
                matched = True
                break
        if not matched:
            log_counter["Unmatched"] += 1
            print(line)

# Display results
print("Log Categories and Counts:")
for category, count in log_counter.items():
    print(f"{category}: {count}")