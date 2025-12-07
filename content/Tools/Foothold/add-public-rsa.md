+++
title = 'SSH Key Foothold'
categories = ['Foothold']
date = 2025-12-07T20:51:00+01:00
+++

# Seamless Foothold with SSH Keys (id_rsa + id_rsa.pub)

Using SSH key-based auth is a clean, reliable way to gain and retain access during CTFs when you have a valid user account or write access to `~/.ssh/authorized_keys` on the target. Below is a fast, repeatable workflow to generate keys, install your public key on the victim, and log in without a password.

> Ethical note: Only use these steps on systems you own or explicitly have permission to test (e.g., CTF boxes).

## 1) Generate a New SSH Key Pair (Local)

Generate a modern ed25519 key (preferred) or RSA if required by the environment.

```zsh
# ed25519 (recommended)
ssh-keygen -t ed25519 -C "ctf@local" -f ~/.ssh/id_ed25519

# RSA (fallback)
ssh-keygen -t rsa -b 4096 -C "ctf@local" -f ~/.ssh/id_rsa
```

Files created:
- Private key: `~/.ssh/id_ed25519` or `~/.ssh/id_rsa`
- Public key: `~/.ssh/id_ed25519.pub` or `~/.ssh/id_rsa.pub`

Ensure sane permissions:

```zsh
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519 ~/.ssh/id_rsa 2>/dev/null || true
chmod 644 ~/.ssh/id_ed25519.pub ~/.ssh/id_rsa.pub 2>/dev/null || true
```

## 2) Install Your Public Key on the Victim

You need the victim user’s home and write access to `~/.ssh/authorized_keys`. Choose one of the methods below depending on what access you have.

### Option A: ssh-copy-id (simple and safe)

If password auth or temporary access is available:

```zsh
# Using ed25519 key
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@victim

# Or with RSA
ssh-copy-id -i ~/.ssh/id_rsa.pub user@victim
```

This creates `~/.ssh` if needed and appends your public key to `authorized_keys` with correct permissions.

### Option B: Manual append via SSH

If you can SSH in with a password or a temporary shell:

```zsh
cat ~/.ssh/id_ed25519.pub | ssh user@victim 'mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'
```

Swap the public key file path if you’re using RSA.

### Option C: Manual write on the victim

Already have a shell on the victim (reverse shell, web shell, or local user)? Echo the public key directly:

```zsh
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA... ctf@local" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

Replace the key blob with the content from your `~/.ssh/id_ed25519.pub` (or `~/.ssh/id_rsa.pub`).

## 3) Verify Permissions (Critical)

OpenSSH is strict: wrong permissions break auth.

```zsh
# On victim
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chown -R user:user ~/.ssh
```

If `authorized_keys` is world-writable or owned by another user, SSH will refuse to use it.

## 4) Log In with Your Key

```zsh
# ed25519 key
ssh -i ~/.ssh/id_ed25519 user@victim

# RSA key
ssh -i ~/.ssh/id_rsa user@victim
```

If you added the key under the default names, you can often omit `-i`:

```zsh
ssh user@victim
```

## 5) Quality-of-Life Tips

- Use `/etc/hosts` for clean names during testing:

```zsh
sudo sh -c 'printf "\n10.82.186.54 cybershield.nc3\n" >> /etc/hosts'
# Then
ssh user@cybershield.nc3
```

- Agent forwarding (when needed):

```zsh
ssh -A user@victim
```

- Keep multiple keys organized via `~/.ssh/config`:

```zsh
cat >> ~/.ssh/config <<'EOF'
Host cybershield.nc3
   HostName 10.82.186.54
   User user
   IdentityFile ~/.ssh/id_ed25519
   IdentitiesOnly yes
EOF
```

Then simply:

```zsh
ssh cybershield.nc3
```

## 6) Troubleshooting

- "Permission denied (publickey)": Check ownership and permissions on `~/.ssh` and `authorized_keys`.
- Wrong user/home: Ensure you installed the key under the exact account you SSH into.
- SSHD config: `PasswordAuthentication`/`PubkeyAuthentication` or `AuthorizedKeysFile` may be customized; review `/etc/ssh/sshd_config` if you have access.
- SELinux/AppArmor: On hardened boxes, security contexts can block auth—set proper contexts if applicable.

With your public key in `authorized_keys`, SSH becomes frictionless and robust—perfect for maintaining a foothold and focusing on the actual challenge.