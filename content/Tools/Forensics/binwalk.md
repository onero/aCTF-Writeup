+++
title = 'binwalk'
categories = ['Forensics']
date = "2026-08-23T15:15:00+01:00"
scrollToTop = true
+++

# binwalk: Finding What's Hidden Inside a File

Files lie about where they end. A JPEG can have a ZIP archive glued to its tail, a firmware image is really a dozen filesystems stacked back-to-back, and a "picture" might be three files in a trenchcoat. [binwalk](https://github.com/ReFirmLabs/binwalk) scans a file for the *signatures* of other file formats embedded anywhere inside it, then extracts them. It's the go-to tool for firmware analysis and for the classic "there's more to this file than meets the eye" forensics/OSINT puzzle.

*Business Trip* in Brunner 2026 is a textbook case: the image carried trailing data past its logical end, and confirming/extracting it is exactly what binwalk is for.

## Installation

```bash
# Debian/Ubuntu
sudo apt install binwalk
# pip (latest)
python3 -m pip install binwalk
```

For extraction of exotic formats you'll also want the helpers binwalk shells out to: `p7zip-full`, `unrar`, `jefferson`, `sasquatch`, etc. On Kali most are already present.

## Step 1: Signature scan

Run binwalk with no flags to get a map of every recognised signature and its offset:

```bash
binwalk suspicious.jpg
```

```text
DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
0             0x0             JPEG image data, JFIF standard 1.01
...
34816         0x8800          Zip archive data, at least v2.0 to extract
34970         0x889A          End of Zip archive
```

That second entry is the tell: a ZIP living *inside* a JPEG. The `DECIMAL` offset is where it starts — everything you need to carve it out. (In *Business Trip* it was trailing archive data past the image; a plain `tail` first hinted at it, and binwalk confirmed and located it precisely.)

## Step 2: Extract

`-e` auto-extracts every known signature into a `_<filename>.extracted/` directory:

```bash
binwalk -e suspicious.jpg
ls _suspicious.jpg.extracted/
```

If auto-extract is stubborn (binwalk is conservative about what it will carve), pull the region yourself with `dd` using the offset from the scan:

```bash
dd if=suspicious.jpg of=hidden.zip bs=1 skip=34816
unzip hidden.zip
```

For recursive extraction of nested containers (firmware within firmware), add `-M` (Matryoshka) — but bound the depth with `-d` so it doesn't explode:

```bash
binwalk -Me --depth=3 firmware.bin
```

## Step 3: Entropy analysis

Not sure whether a blob is compressed, encrypted, or plain data? An entropy graph tells you:

```bash
binwalk -E suspicious.bin        # entropy scan
```

Flat high entropy (~1.0) across a region means compressed or encrypted content; sharp transitions often mark boundaries between a header and a packed payload — useful for spotting where an embedded object begins even when there's no clean signature.

## Where binwalk fits with other tools

binwalk finds *structured* embedded files. Pair it with:

- **`tail` / `xxd`** — a quick manual check for trailing bytes after a format's end marker (`FF D9` for JPEG, `IEND` for PNG). Often the first hint before you even run binwalk.
- **`strings | grep`** — for embedded text, URLs, or a flag that isn't a whole file.
- **`foremost` / `scalpel`** — dedicated file-carvers that can succeed where binwalk's extractor balks.
- **`exiftool`** — metadata that binwalk ignores; run both, they answer different questions.

For *Business Trip* this whole cluster was in play — `tail` to notice the trailing archive, binwalk to locate and extract it, `strings | grep` to sweep for leftover text.

## A caution

binwalk's signature matching produces **false positives** — random data will occasionally look like the start of some obscure format. Treat the scan as leads to verify, not gospel: a "LZMA compressed data" hit at a weird offset with nothing extractable is usually noise. Confirm by actually extracting and opening the result.

> Security note: historic binwalk versions had extraction vulnerabilities (path traversal via crafted archives). Extract untrusted files in a throwaway directory or container, and keep binwalk updated.

## Best practices

- **Scan before you extract.** The offset map tells you *what* is inside and *where*, so you can carve precisely with `dd` if `-e` won't.
- **Check the tail manually too.** A five-second `tail -c 200 file | xxd` catches appended data that a signature scan might not flag as a clean format.
- **Bound recursion.** `-Me` without `--depth` on a real firmware image will bury you in extracted junk.
- **Verify hits.** Open what you extracted; don't trust a signature label alone.

## Conclusion

Whenever a file feels heavier than it looks — an image that's too big, a "document" that won't fully render, firmware you need to crack open — binwalk is the first question to ask: *what else is in here?* Scan, read the offsets, extract, verify. More often than not, the flag was riding along past the end of the file all along. Happy carving!
