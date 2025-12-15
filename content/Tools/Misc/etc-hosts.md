+++
title: "Pretty Hostnames with /etc/hosts"
categories: ['Misc']
date: "2025-12-07T20:22:53+01:00"
scrollToTop = true
+++

When attacking or enumerating a target, typing raw IPs everywhere is clunky and error-prone. A simple, built-in trick is to use `/etc/hosts` to map an IP address to a friendly hostname so your tools, browser, and shell can use a memorable name.

Example mapping:

```
10.82.186.54 cybershield.nc3
```

This lets you visit `http://cybershield.nc3` in your browser, curl `cybershield.nc3`, and point tools at the hostname instead of the IP.

**What /etc/hosts Does**
- Local override: Maps hostnames to IPs before DNS is queried.
- Zero dependencies: No DNS server required; works offline.
- System-wide: Applies to all applications on the machine.

**How to Add an Entry (macOS/Linux)**
- Edit the hosts file with elevated privileges:

```zsh
sudo sh -c 'printf "\n10.82.186.54 cybershield.nc3\n" >> /etc/hosts'
```

- Or open it in an editor:

```zsh
sudo vim /etc/hosts
# Add the line:
# 10.82.186.54 cybershield.nc3
```

**Verify the Mapping**
- Resolve the hostname:

```zsh
ping -c 1 cybershield.nc3
```

- Check with `getent` (Linux) or `dscacheutil` (macOS):

```zsh
# Linux
getent hosts cybershield.nc3

# macOS
dscacheutil -q host -a name cybershield.nc3
```

**Use It Everywhere**
- Browser: Visit `http://cybershield.nc3`.
- CLI: `curl -I cybershield.nc3`, `nc cybershield.nc3 80`, `ssh user@cybershield.nc3`.
- Tools: Nmap, Gobuster, ffuf, sqlmap, etc. accept hostnames:

```zsh
nmap -sV cybershield.nc3
gobuster dir -u http://cybershield.nc3 -w wordlist.txt
ffuf -u http://cybershield.nc3/FUZZ -w wordlist.txt
```

**Tips & Best Practices**
- Keep entries tidy: Group targets and add comments with context.
- Include multiple names: Add aliases on the same line if helpful:

```
10.82.186.54 cybershield.nc3 shield nc3-shield
```

- Subdomains: Add each needed subdomain explicitly:

```
10.82.186.54 www.cybershield.nc3 admin.cybershield.nc3 api.cybershield.nc3
```

- IPv6 targets: Use the IPv6 address format on separate lines.
- Avoid collisions: Pick unique names unlikely to be real public domains.
- Reset when done: Remove entries to avoid future confusion.

**Troubleshooting**
- Entry not working? Check for typos, extra spaces, or hidden characters.
- Conflicts: If DNS still wins, ensure no trailing domain search suffix alters the name.
- macOS caching: Flush caches if changes don’t apply immediately:

```zsh
sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
```

**Why This Helps in CTFs**
- Faster commands, cleaner screenshots, and easier collaboration.
- Reduces mistakes when switching between many targets.
- Makes service-specific testing more readable: `admin.cybershield.nc3:8080` beats `10.82.186.54:8080` in clarity.

Add the line, use the name, and enjoy cleaner, faster workflows.

