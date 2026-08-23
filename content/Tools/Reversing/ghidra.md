+++
title = 'Ghidra'
categories = ['Reversing']
date = "2026-08-23T14:15:00+01:00"
scrollToTop = true
+++

# Ghidra: Reading a Binary Like Source Code

[Ghidra](https://ghidra-sre.org/) is the free, open-source reverse-engineering suite released by the NSA. Its headline feature is a genuinely excellent **decompiler** that turns compiled machine code back into readable C-like pseudocode — for most challenges it's the difference between squinting at assembly for an hour and reading the logic in five minutes. It's the tool I reach for first on any reversing binary, and it's what cracked *Go Go Decompile* in the Brunner 2026 set.

## Installation

Ghidra is a Java application, so you need a JDK (21+ for recent releases).

- **Download** the latest release from [the GitHub releases page](https://github.com/NationalSecurityAgency/ghidra/releases) (a zip, no installer).
- **Java:** install a JDK, e.g. `sudo apt install openjdk-21-jdk` on Debian/Ubuntu or `brew install openjdk@21` on macOS.
- **Run:** unzip and launch:

```bash
unzip ghidra_*.zip
cd ghidra_*/
./ghidraRun          # ghidraRun.bat on Windows
```

## The basic workflow

### 1. Create a project and import the binary

Ghidra organises work into *projects*. On first launch:

1. `File → New Project → Non-Shared Project`, pick a folder and a name.
2. Drag your binary into the project window (or `File → Import File`). Ghidra auto-detects the format (ELF, PE, Mach-O, raw).
3. Double-click the imported file to open it in the **CodeBrowser**.

### 2. Let auto-analysis run

When you open a binary, Ghidra offers to analyze it — say **Yes** and accept the defaults for a first pass. Auto-analysis disassembles the code, identifies functions, resolves cross-references, and recovers strings. On a small CTF binary this takes seconds.

### 3. Navigate

The windows you'll live in:

- **Symbol Tree** (left) — functions, labels, imports, exports. Jump straight to `main` or `entry`.
- **Listing** (centre) — the disassembly, annotated with comments and xrefs.
- **Decompiler** (right) — the C-like reconstruction of whatever function you're viewing. This is the star.
- **Defined Strings** (`Window → Defined Strings`) — every string Ghidra found. Often the fastest route into a challenge: find the "Correct!" string, then follow its cross-reference back to the check.

### 4. Follow the logic

Double-click a function to decompile it. Then:

- Press **`L`** to rename a variable or function to something meaningful (`local_18` → `user_input`). Renames propagate everywhere.
- Press **`Ctrl+L`** to retype a variable (e.g. tell Ghidra a `void *` is actually a `char[16]`) — the decompilation often clarifies dramatically once types are right.
- Press **`;`** to add an inline comment.
- Right-click → **References → Find References to** (or press **`Ctrl+Shift+F`**) to see every place a function/string/address is used. This is how you work backwards from a flag-check string to the code that calls it.

## Extracting data tables from .rodata

A recurring reversing pattern — and exactly what *Go Go Decompile* and *KPwhy* came down to — is that the interesting data (an encoded flag, a lookup table, a set of constants) sits in `.rodata`, and the code just indexes into it. In Ghidra:

1. Find the reference in the decompiler (e.g. `puts(&DAT_004c8f20)` or an array base address).
2. Double-click the address to jump to it in the Listing.
3. Select the bytes and `Right-click → Copy Special → Byte String` to pull them out, or note the virtual address and carve them from the file directly.

For scripted extraction you often want the **file offset** rather than the virtual address. Ghidra shows both, but you can also compute it once you know the section layout (`readelf -S ./bin` gives the vaddr→file-offset delta for `.rodata`), then read the bytes in Python for further processing:

```python
with open('bin', 'rb') as f:
    f.seek(FILE_OFFSET)
    table = f.read(LENGTH)
import base64
print(base64.b64decode(table))   # e.g. Go Go Decompile stashed a base64 blob here
```

## Go binaries: a word of warning

*Go Go Decompile* was a Go binary, and Go is deliberately awkward to reverse:

- The Go runtime is enormous — thousands of functions dwarf the handful you care about. Use the **Symbol Tree** filter and jump straight to `main.main`, `main.*` functions.
- Go binaries are usually **not stripped of Go metadata**, so `nm ./bin | grep main` and `objdump --disassemble=main.main -M intel ./bin` are excellent companions to Ghidra for pinpointing the real entry logic before you commit to decompiling.
- Calling conventions and string handling (pointer + length, not null-terminated) confuse the decompiler; expect to retype things and read strings by their length field.

Ghidra ships with Go analysis improvements in recent versions, but pairing it with `nm`/`objdump` remains the fastest way in.

## Handy extras

- **Function Graph** (`Window → Function Graph`) — a visual CFG, great for untangling nested branches in a flag checker.
- **Patch + export** — you can patch instructions (`Ctrl+Shift+G`) and export a modified binary, useful for NOP-ing out an anti-debug check.
- **Scripting** — the Script Manager runs Java or Python (Jython/PyGhidra) scripts against the analysis database for bulk extraction.
- **Version tracking / BSim** — for comparing binaries or finding known library functions in stripped code.

## Best practices

- **Rename as you understand.** A function full of `local_*` is unreadable; five minutes of renaming turns it into pseudocode you can reason about.
- **Start from strings and imports.** The shortest path to the vulnerable/checking code is almost always a cross-reference from a recognisable string or a call to `strcmp`/`memcmp`/`system`.
- **Verify by re-implementing.** Once you think you understand the check (as with *KPwhy*'s XOR/running-sum chain), re-implement it in Python and confirm it reproduces the expected output before trusting your reading.
- **Keep the raw tools handy.** `file`, `nm`, `strings`, and `objdump` answer "what am I even looking at" faster than booting the GUI.

## Conclusion

Ghidra flattens the learning curve of reverse engineering more than any other free tool. You won't understand every binary at a glance, but between the decompiler, cross-references, and a bit of renaming discipline, you'll turn most CTF reversing challenges from an assembly slog into a reading exercise. Import the binary, hit analyze, and start renaming. Happy reversing!
