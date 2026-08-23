+++
title = 'ExifTool'
categories = ['OSINT']
date = "2026-08-23T15:00:00+01:00"
scrollToTop = true
+++

# ExifTool: Squeezing Metadata Out of Files

Every photo, PDF, and document carries a surprising amount of hidden metadata — camera model, software, timestamps, edit history, and, most usefully for OSINT, **GPS coordinates**. [ExifTool](https://exiftool.org/) by Phil Harvey is the definitive tool for reading (and writing) this metadata across essentially every file format that has any. In an OSINT or forensics challenge it's usually the very first command you run, because the answer is often sitting in a tag the challenge author forgot to strip.

This guide leans on *Business Trip* from Brunner 2026, a geolocation challenge that started with an image's embedded metadata.

## Installation

```bash
# Debian/Ubuntu
sudo apt install libimage-exiftool-perl
# macOS
brew install exiftool
# Windows: download the standalone .exe from exiftool.org
```

The command is `exiftool` (some distros symlink `exiftool` → the perl script).

## The first command: dump everything

Point it at a file and read the lot:

```bash
exiftool image.jpg
```

For OSINT work the flags that matter are the ones that show you *where* each tag comes from and leave nothing hidden:

```bash
exiftool -a -G1 -s image.jpg
```

- `-a` — show **all** tags, including duplicates.
- `-G1` — prefix each tag with its **group** (e.g. `[GPS]`, `[EXIF]`, `[ICC_Profile]`, `[XMP]`), so you can see whether data came from EXIF, an ICC colour profile, XMP, or a maker note.
- `-s` — short tag names (the machine-readable form you'd use to query a single tag).

This is exactly the sweep that opens *Business Trip*: dump every group, and scan for anything the author left behind — GPS, a software fingerprint, an ICC profile hinting at the capture device.

## Going straight for GPS

If the image is geotagged, you've essentially won a geolocation challenge:

```bash
exiftool -gpslatitude -gpslongitude -gpsposition image.jpg
# decimal degrees, ready to paste into a map:
exiftool -n -gpslatitude -gpslongitude image.jpg
exiftool -c "%.6f" -GPS:all image.jpg          # formatted to 6 decimal places
```

Drop the resulting `lat, long` straight into Google Maps. Even without a precise fix, GPS altitude, direction (`GPSImgDirection`), and timestamp narrow things down fast.

## Other high-value tags

- **Timestamps** — `DateTimeOriginal`, `CreateDate`, `ModifyDate`. Discrepancies reveal editing; the original often survives even when the file was re-saved.
- **Software / Device** — `Make`, `Model`, `Software`, `LensModel`. "Edited with Photoshop on macOS" is a lead in itself.
- **ICC profile** — colour-management data that can fingerprint the capturing device or software.
- **Thumbnail** — cameras embed a thumbnail that is sometimes *not* re-rendered after a crop, occasionally leaking the pre-crop image. Extract it:

```bash
exiftool -b -ThumbnailImage image.jpg > thumb.jpg
```

## Reading many files or other formats

ExifTool isn't just for JPEGs — it reads PDFs, Office docs, videos, and more:

```bash
exiftool *.jpg                    # batch a whole directory
exiftool -r -Author -Creator .    # recurse, pull document authors from PDFs/docs
exiftool document.pdf             # PDF producer/creator/modify history
```

## Writing and stripping (the defensive side)

Worth knowing, if only to understand what challenge authors *should* have done:

```bash
exiftool -all= image.jpg               # strip all metadata (blue-team hygiene)
exiftool -GPS:all= image.jpg           # remove only location data
exiftool -DateTimeOriginal="2026:01:01 12:00:00" image.jpg   # set a tag
```

## Combine it with other tools

ExifTool reads structured metadata, but files often hide data *beyond* the metadata block — appended archives, extra data after the image's logical end. When a metadata sweep comes up short, that's your cue to reach for `binwalk`, `strings | grep`, or a simple `tail` to check for trailing content (all part of the *Business Trip* toolkit). ExifTool tells you what the file *admits*; those tools find what it's hiding.

## Best practices

- **Run `exiftool -a -G1 -s` on everything first.** It's non-destructive and often ends the challenge on the spot.
- **Trust the original timestamp over the modify time.** `DateTimeOriginal` frequently survives re-saves that scrub other tags.
- **Convert GPS to decimal (`-n` or `-c`)** before pasting into a map to avoid DMS-vs-decimal confusion.
- **Don't stop at metadata.** No GPS ≠ no location — fall back to reverse image search and visual geolocation (terrain, signage, architecture), which is how *Business Trip* was ultimately pinned down.

## Conclusion

ExifTool is the OSINT reflex: before you squint at the pixels, ask the file what it already knows about itself. More often than you'd expect, the flag — or the coordinates that lead to it — is one `exiftool -a -G1 -s` away. Happy hunting!
