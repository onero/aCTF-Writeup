+++
title = 'Matching the Remote with Docker (glibc pinning)'
categories = ['Pwn']
date = "2026-08-23T14:30:00+01:00"
description = "Match a pwn challenge's remote environment by extracting the exact glibc and loader from its Docker image, patching the binary, and wiring it into pwntools."
tags = ["glibc", "docker", "pwn", "pwntools", "reverse-engineering"]
scrollToTop = true
+++

# Matching the Remote with Docker: glibc Pinning for Pwn

Here's the failure mode that eats hours: your exploit works flawlessly on your machine, then does nothing against the remote. Nine times out of ten the culprit is the **C library**. libc offsets — the distance from a leaked `puts` to `system`, from `system` to a `/bin/sh` string, the exact `one_gadget` constraints — are *specific to the exact glibc build* on the target. Your local Ubuntu's libc is almost never byte-identical to the challenge's.

The fix is to stop guessing and run the challenge locally against the *exact same libc* the server uses. Modern pwn challenges ship a `Dockerfile`, which tells you precisely how to reproduce their environment. This workflow underpinned every heap challenge in the Brunner 2026 set — *Pure Notes* (glibc 2.41), *Guessing Game*, *Roadmap*, and *Mindbreaker* all hinged on getting the environment right first.

## Step 1: Read the Dockerfile

The handout's `Dockerfile` is a free spec sheet. The base image pins the glibc version:

```dockerfile
FROM ubuntu:24.04          # <- Ubuntu 24.04 ships glibc 2.39
# or
FROM ubuntu:25.04          # <- ships glibc 2.41 (this is what Pure Notes used)
```

If there's no Dockerfile but you were given a `libc.so.6`, skip to Step 4 — you already have the artefact that matters. Check its version directly:

```bash
./libc.so.6                       # prints "GNU C Library ... release version 2.41"
strings libc.so.6 | grep "GNU C"  # if it isn't executable
```

## Step 2: Build and run the challenge locally

Reproduce the server on your own box so local testing behaves like remote:

```bash
docker build -t chal .
docker run --rm -p 1024:1024 chal        # now `nc localhost 1024` hits your copy
```

Now you can develop your pwntools exploit against `remote('localhost', 1024)` with identical behaviour to the real target — no ASLR/libc surprises when you switch over.

## Step 3: Extract the exact libc and loader from the container

To run the binary *directly* (for GDB, `one_gadget`, offset work) you need the container's `libc.so.6` and its dynamic loader `ld-linux-x86-64.so.2`:

```bash
# start the container, then copy the files out
id=$(docker create chal)
docker cp "$id":/lib/x86_64-linux-gnu/libc.so.6 ./libc.so.6
docker cp "$id":/lib64/ld-linux-x86-64.so.2 ./ld.so
docker rm "$id"
```

(Paths vary; `docker run --rm -it chal bash` and `ldd /path/to/challenge` will show you exactly which libc/loader the binary uses.)

## Step 4: Patch the binary to use that libc

The cleanest tool is [`pwninit`](https://github.com/io12/pwninit): drop the challenge binary, `libc.so.6`, and `ld` in a directory and run it — it patches the binary's interpreter and RPATH and even fetches matching debug symbols:

```bash
pwninit          # produces ./vuln_patched
```

Prefer to do it by hand? `patchelf` is the underlying mechanism:

```bash
patchelf --set-interpreter ./ld.so --replace-needed libc.so.6 ./libc.so.6 ./vuln
# or set an RPATH so the loader finds the local libc:
patchelf --set-rpath . ./vuln
```

Either way, `ldd ./vuln` should now point at *your* extracted `libc.so.6`. You're now running bit-for-bit what the server runs.

## Step 5: Wire it into pwntools and one_gadget

Point your exploit at the matched libc so every offset is computed against the right build:

```python
from pwn import *
context.binary = elf = ELF('./vuln_patched')
libc = ELF('./libc.so.6')                       # the extracted one

io = process([elf.path])                        # runs with the patched interpreter
# ... leak a libc address, e.g. from puts@GOT ...
libc.address = leak - libc.symbols['puts']      # rebase the whole libc
system = libc.symbols['system']
binsh  = next(libc.search(b'/bin/sh\x00'))
```

And run [`one_gadget`](https://github.com/david942j/one_gadget) against the *exact* libc — its magic `execve("/bin/sh")` offsets and their register/stack constraints differ between builds, which is why running it on your system libc gives you an address that segfaults remotely:

```bash
one_gadget ./libc.so.6
# 0xddf83 execve("/bin/sh", ...)  constraints: ...
```

(*Guessing Game* is a cautionary tale here: a `one_gadget` looked perfect but its constraints never held under the challenge's stack layout, so we fell back to a classic `pop rdi; ret` → `system("sh")` chain. Having the exact libc is what let us *see* that quickly instead of blaming the wrong thing.)

## When there's no handout binary at all

*Guessing Game* gave no source and no binary — just a TLS endpoint and a stated glibc version. Even then the workflow holds: spin up the matching Ubuntu image, `apt-get` the same glibc, and copy its `libc.so.6` out to run `one_gadget` and compute offsets. Knowing the version is enough to reconstruct the library.

```bash
docker run --rm -it ubuntu:25.04 bash
# inside: apt-get update && apt-get install -y libc6   (already present)
# then docker cp the libc out as in Step 3
```

## Best practices

- **Match before you debug.** Don't touch offsets until `ldd` confirms your binary is loading the target's libc. Otherwise you're debugging the wrong library.
- **Keep the loader too.** A mismatched `ld.so` and `libc.so.6` will refuse to run or behave subtly wrong — always extract both.
- **Version, not distro.** "Ubuntu 24.04" is shorthand; what matters is `glibc 2.39`. Two distros on the same glibc are interchangeable for this purpose.
- **Re-run `one_gadget` per libc.** Never reuse a gadget offset across challenges; regenerate it against each target's library.

## Conclusion

Environment parity is the unglamorous half of binary exploitation, and skipping it is the most common reason a "correct" exploit fails remotely. Read the Dockerfile, extract the libc and loader, patch the binary, and point pwntools and `one_gadget` at the real thing. Do this first and the exploit-development part becomes honest: if it works locally, it works remotely. Happy pwning!
